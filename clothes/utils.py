# mindvibe_full/clothes/utils.py

import libscrc
import qrcode
from PIL import Image
import io
from typing import Union, Optional, Tuple

# --- EMVCo Tag Constants ---
TAG_PAYLOAD_FORMAT_INDICATOR = "00"
TAG_POINT_OF_INITIATION_METHOD = "01"
TAG_MERCHANT_ACCOUNT_INFORMATION = "29"
# Sub-tags for Merchant Account Information (Tag 29 - PromptPay specific context)
SUB_TAG_AID_PROMPTPAY = "00"
SUB_TAG_MOBILE_NUMBER_PROMPTPAY = "01"
SUB_TAG_NATIONAL_ID_PROMPTPAY = "02"

TAG_TRANSACTION_CURRENCY = "53"
TAG_TRANSACTION_AMOUNT = "54" # Optional if amount is zero or not specified
TAG_COUNTRY_CODE = "58"
TAG_CRC = "63"

# --- Standard Values ---
VALUE_PAYLOAD_FORMAT_INDICATOR = "01"    # Version 1 of the EMVCo QR standard
VALUE_POINT_OF_INITIATION_MULTIPLE = "11" # Static QR for multiple uses
VALUE_POINT_OF_INITIATION_ONETIME = "12"  # QR for one-time use
VALUE_PROMPTPAY_AID = "A000000677010111" # Specific AID for PromptPay
VALUE_COUNTRY_CODE_TH = "TH"             # Thailand
VALUE_CURRENCY_THB = "764"               # Thai Baht (ISO 4217 numeric)

# --- Fixed Lengths for Certain Field Values or LL part of TLV ---
LEN_CRC_VALUE_HEX = "04" # Length of the CRC value itself (4 hex characters)

class QRError(Exception):
    """Custom base exception for QR generation errors."""
    pass

class InvalidInputError(QRError):
    """Custom exception for invalid input values."""
    pass

def _format_tlv(tag: str, value: str) -> str:
    """
    Formats a Tag-Length-Value (TLV) string.
    The length is a 2-digit zero-padded string representing the byte length of the value.
    """
    if not isinstance(value, str):
        raise TypeError(f"TLV value for tag {tag} must be a string, got {type(value)}.")
    length_str = f"{len(value):02d}"
    return f"{tag}{length_str}{value}"

def calculate_crc(code_string: str) -> str:
    """
    Calculates the CRC16 (CCITT-FALSE variant) for the given code string.
    `libscrc.ccitt_false` uses poly=0x1021, init=0xFFFF, refin=False, refout=False, xorout=0x0000.
    This matches the common requirement for EMVCo QR CRC.
    """
    try:
        encoded_string = str.encode(code_string, 'ascii')
    except UnicodeEncodeError:
        raise InvalidInputError("Payload contains non-ASCII characters, which is not supported for CRC calculation.")

    crc_val = libscrc.ccitt_false(encoded_string) # type: ignore
    crc_hex_str = hex(crc_val)[2:].upper() # Remove "0x" and uppercase
    return crc_hex_str.rjust(4, '0') # Zero-pad to 4 characters

def generate_promptpay_qr_payload(
    mobile: Optional[str] = None,
    nid: Optional[str] = None,
    amount: Optional[Union[float, int, str]] = None,
    one_time: bool = False) -> str:
    """
    Generates the full PromptPay QR code payload string according to EMVCo standards.
    """
    if not mobile and not nid:
        raise InvalidInputError("Either mobile number or National ID (NID) must be provided.")
    if mobile and nid:
        raise InvalidInputError("Provide either mobile number or National ID (NID), not both.")

    payload_elements = []

    payload_elements.append(
        _format_tlv(TAG_PAYLOAD_FORMAT_INDICATOR, VALUE_PAYLOAD_FORMAT_INDICATOR)
    )

    initiation_method_value = VALUE_POINT_OF_INITIATION_ONETIME if one_time else VALUE_POINT_OF_INITIATION_MULTIPLE
    payload_elements.append(
        _format_tlv(TAG_POINT_OF_INITIATION_METHOD, initiation_method_value)
    )

    merchant_account_sub_elements = []
    merchant_account_sub_elements.append(_format_tlv(SUB_TAG_AID_PROMPTPAY, VALUE_PROMPTPAY_AID))

    if mobile:
        mobile_cleaned = mobile.strip()
        if not (len(mobile_cleaned) == 10 and mobile_cleaned.isdigit()):
            raise InvalidInputError("Mobile number must be a 10-digit string (e.g., '0812345678').")
        # For mobile, the PromptPay spec usually uses the format "0066" followed by mobile number without leading zero.
        # However, the provided code uses a slightly different format. Sticking to the provided code's logic.
        formatted_mobile_value = f"00{VALUE_COUNTRY_CODE_TH}{mobile_cleaned[1:]}" # Example: 00TH812345678
        merchant_account_sub_elements.append(
            _format_tlv(SUB_TAG_MOBILE_NUMBER_PROMPTPAY, formatted_mobile_value)
        )
    elif nid:
        nid_cleaned = nid.strip().replace('-', '')
        if not (len(nid_cleaned) == 13 and nid_cleaned.isdigit()):
            raise InvalidInputError("National ID (NID) must be a 13-digit string (e.g., '1234567890123').")
        merchant_account_sub_elements.append(
            _format_tlv(SUB_TAG_NATIONAL_ID_PROMPTPAY, nid_cleaned)
        )
    payload_elements.append(
        _format_tlv(TAG_MERCHANT_ACCOUNT_INFORMATION, "".join(merchant_account_sub_elements))
    )

    payload_elements.append(
        _format_tlv(TAG_TRANSACTION_CURRENCY, VALUE_CURRENCY_THB)
    )

    if amount is not None:
        amount_str_eval = str(amount).strip()
        if amount_str_eval: # Ensure it's not an empty string after strip
            try:
                amount_float = float(amount_str_eval)
                if amount_float < 0: # Allow 0.00 for open amount QR
                    raise InvalidInputError("Transaction amount cannot be negative.")
                # Format to 2 decimal places, as per EMVCo for currency
                formatted_amount_value = f"{amount_float:.2f}"
                payload_elements.append(_format_tlv(TAG_TRANSACTION_AMOUNT, formatted_amount_value))
            except ValueError:
                raise InvalidInputError(f"Invalid amount value: '{amount}'. Must be a number.")

    payload_elements.append(
        _format_tlv(TAG_COUNTRY_CODE, VALUE_COUNTRY_CODE_TH)
    )

    data_for_crc_calculation = "".join(payload_elements)
    string_to_calculate_crc_on = data_for_crc_calculation + TAG_CRC + LEN_CRC_VALUE_HEX
    crc_hex_value = calculate_crc(string_to_calculate_crc_on)
    final_payload_string = string_to_calculate_crc_on + crc_hex_value
    return final_payload_string.upper()

def generate_promptpay_qr_image_data(
    mobile: Optional[str] = None,
    nid: Optional[str] = None,
    amount: Optional[Union[float, int, str]] = None,
    one_time: bool = False,
    box_size: int = 10,
    border: int = 4) -> Optional[bytes]:
    """
    Generates a PromptPay QR payload and returns the QR image as PNG bytes.

    Args:
        mobile: 10-digit Thai mobile number.
        nid: 13-digit Thai National ID or Tax ID.
        amount: The transaction amount.
        one_time: If True, QR is for single use. Defaults to False.
        box_size: Controls how many pixels each “box” of the QR code is.
        border: Controls how many boxes thick the border should be.
    Returns:
        Bytes of the PNG image, or None if an error occurs.
    """
    try:
        payload = generate_promptpay_qr_payload(mobile=mobile, nid=nid, amount=amount, one_time=one_time)
        # print(f"Generated Payload: {payload}") # For debugging

        qr_img_obj = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=box_size,
            border=border,
        )
        qr_img_obj.add_data(payload)
        qr_img_obj.make(fit=True)

        img = qr_img_obj.make_image(fill_color="black", back_color="white")

        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    except QRError as e:
        print(f"Error generating QR code: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None