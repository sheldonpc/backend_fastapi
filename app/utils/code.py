import random
import string

def generate_verification_code(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=length))

# 测试
if __name__ == "__main__":
    print(generate_verification_code())