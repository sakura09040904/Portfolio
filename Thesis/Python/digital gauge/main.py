import os
from PIL import Image

# 이미지 소스 디렉토리 지정
current_directory = 'src'

# 이미지 저장 디렉토리 설정
output_directory = 'D:/Portfolio/Thesis/Python/digital gauge/output'
os.makedirs(output_directory, exist_ok=True)  # 출력 폴더가 없으면 생성

# 소스 이미지 및 숫자 이미지 로드
source_image_path = os.path.join(current_directory, 'source.png')
source_image = Image.open(source_image_path)

# 0~9 이미지 객체 생성
number_images = {}  
for i in range(10):
    file_path = os.path.join(current_directory, f'{i}.png')  # 각 숫자에 해당하는 파일 경로를 생성합니다.
    image = Image.open(file_path)  # 이미지 파일을 열어 이미지 객체를 생성합니다.
    number_images[str(i)] = image  # 생성된 이미지 객체를 딕셔너리에 저장합니다.



# 숫자 크기 조정 함수
def resize_digit(image, target_height):
    w, h = image.size
    proportion = target_height / h
    new_size = (int(w * proportion), target_height)
    return image.resize(new_size, Image.Resampling.LANCZOS)

#숫자 이미지 resizeing
resized_digits = {}  
for k, v in number_images.items():
    resized_image = resize_digit(v, 75) 
    resized_digits[k] = resized_image  


# 숫자 위치 조정
base_x = 140
base_y = 150
gap = 32 #간격

#각 숫자 자리수별 위치,간격
digit_positions = {
    'hundreds': (base_x, base_y),
    'tens': (base_x + gap, base_y),
    'one': (base_x + 2 * gap, base_y),
    'tenths': (base_x + 3 * gap, base_y),
    'hundredths': (base_x + 4 * gap, base_y)
}

# 모든 가능한 숫자 조합 생성 및 이미지 저장
for i in range(1000):  # 000 to 999 소수점 위
    for j in range(100):  # 00 to 99 소수점 아래
        test_image = source_image.copy()
        # 각 숫자 위치 합성
        numbers = f"{i:03d}.{j:02d}"
        test_image.paste(resized_digits[numbers[0]], digit_positions['hundreds'], resized_digits[numbers[0]])
        test_image.paste(resized_digits[numbers[1]], digit_positions['tens'], resized_digits[numbers[1]])
        test_image.paste(resized_digits[numbers[2]], digit_positions['one'], resized_digits[numbers[2]])
        test_image.paste(resized_digits[numbers[4]], digit_positions['tenths'], resized_digits[numbers[4]])
        test_image.paste(resized_digits[numbers[5]], digit_positions['hundredths'], resized_digits[numbers[5]])
        
        # 파일 저장
        file_name = f"{numbers}.png"
        output_path = os.path.join(output_directory, file_name)
        test_image.save(output_path)
        print(f"{i:03d}.{j:02d}이 저장되었습니다.")

print("모든 이미지가 생성되었습니다.")
