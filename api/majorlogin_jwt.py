import requests
import binascii
import jwt
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import my_pb2
import output_pb2

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV = b'6oyZDr22E3ychjM%'

def encrypt_message(plaintext):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded_message = pad(plaintext, AES.block_size)
    return cipher.encrypt(padded_message)

def handler(request):
    access_token = request.args.get('access_token')
    open_id = request.args.get('open_id')
    platform_type = request.args.get('platform_type')

    if not access_token or not open_id or not platform_type:
        return {"message": "missing access_token, open_id, platform_type"}, 400

    try:
        platform_type = int(platform_type)
    except ValueError:
        return {"message": "invalid platform_type"}, 400

    game_data = my_pb2.GameData()
    game_data.timestamp = "2024-12-05 18:15:32"
    game_data.game_name = "free fire"
    game_data.game_version = 1
    game_data.version_code = "1.108.3"
    game_data.os_info = "Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)"
    game_data.device_type = "Handheld"
    game_data.network_provider = "Verizon Wireless"
    game_data.connection_type = "WIFI"
    game_data.screen_width = 1280
    game_data.screen_height = 960
    game_data.dpi = "240"
    game_data.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
    game_data.total_ram = 5951
    game_data.gpu_name = "Adreno (TM) 640"
    game_data.gpu_version = "OpenGL ES 3.0"
    game_data.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
    game_data.ip_address = "172.190.111.97"
    game_data.language = "en"
    game_data.open_id = open_id
    game_data.access_token = access_token
    game_data.platform_type = platform_type
    game_data.field_99 = str(platform_type)
    game_data.field_100 = str(platform_type)

    serialized_data = game_data.SerializeToString()
    encrypted_data = encrypt_message(serialized_data)
    hex_encrypted_data = binascii.hexlify(encrypted_data).decode('utf-8')

    url = "https://loginbp.ggblueshark.com/MajorLogin"
    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/octet-stream",
        "Expect": "100-continue",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB48"
    }
    edata = bytes.fromhex(hex_encrypted_data)

    try:
        response = requests.post(url, data=edata, headers=headers, verify=False, timeout=5)
    except requests.RequestException as e:
        return {"message": str(e)}, 500

    if response.status_code == 200:
        data_dict = None
        try:
            example_msg = output_pb2.Garena_420()
            example_msg.ParseFromString(response.content)
            data_dict = {field.name: getattr(example_msg, field.name)
                         for field in example_msg.DESCRIPTOR.fields
                         if field.name not in ["binary", "binary_data", "Garena420"]}
        except Exception:
            try:
                data_dict = response.json()
            except ValueError:
                return {"message": response.text}, 200

        if data_dict and "token" in data_dict:
            token_value = data_dict["token"]
            try:
                decoded_token = jwt.decode(token_value, options={"verify_signature": False})
            except Exception as e:
                decoded_token = {"error": str(e)}
        else:
            return {"message": "No token found in response"}, 200

        result = {
            "token": token_value,
            "developer": "@BNGX"
        }
        return result, 200
    else:
        try:
            return response.json(), response.status_code
        except ValueError:
            return {"message": response.text}, response.status_code

