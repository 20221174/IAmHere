from config.config import AES_KEY
from AES256 import *  # AES 암호화 모듈 추가
from fingerprint import *
from db import *

def main():
    initialize_database()

    user_dao = UserDAO()
    student_dao = StudentDAO()
    professor_dao = ProfessorDAO()
    lecture_dao = LectureDAO()
    enrollment_dao = EnrollmentDAO()
    bluetooth_dao = BluetoothDeviceDAO()
    fingerprint_dao = FingerprintDAO()

    aes_cipher = AES256(AES_KEY)  # AES 객체 생성

    while True:
        print("\n===== 메인 메뉴 =====")
        print("1. 사용자 등록")
        print("2. 강의 등록")
        print("3. 수강 신청")
        print("4. 블루투스 장치 수동 추가")
        print("5. 지문 등록")
        print("0. 종료")

        choice = input("선택 (0-5): ").strip()

        if choice == "1":
            login_id = input("아이디 입력: ").strip()
            password = input("비밀번호 입력: ").strip()
            name = input("이름 입력: ").strip()

            roles = {
                '1': 'professor',
                '2': 'student'
            }
            role = None

            while role is None:
                num = input("1번: 교수, 2번: 학생\n번호를 입력하세요: ").strip()
                role = roles.get(num)

                if role == 'professor':
                    user_id = user_dao.add_user(login_id, password, name, 'professor')
                    if user_id is None:
                        print("❌ 사용자 등록 실패")
                        break
                    department = input("담당 학과: ").strip()
                    if professor_dao.add_professor(user_id, department):
                        print("✅ 교수 등록 완료")
                    else:
                        print("❌ 교수 등록 실패")
                    break

                elif role == 'student':
                    user_id = user_dao.add_user(login_id, password, name, 'student')
                    if user_id is None:
                        print("❌ 사용자 등록 실패")
                        break
                    major = input("학과: ").strip()
                    student_number = input("학번: ").strip()
                    if student_dao.add_student(user_id, major, student_number):
                        print("✅ 학생 등록 완료")
                    else:
                        print("❌ 학생 등록 실패")
                    break

                else:
                    print(f"잘못된 입력입니다. 다시 선택해주세요.\n")

            else:
                print("❌ 사용자 등록 실패")

        elif choice == "2":
            title = input("강의명: ").strip()
            day = input("요일 (월~금): ").strip()
            professor_id = input("강의자 ID: ").strip()
            start_time = input("시작 시간 (HH:MM:SS): ").strip()
            end_time = input("종료 시간 (HH:MM:SS): ").strip()
            start_date = input("시작 날짜 (YYYY-MM-DD): ").strip()
            end_date = input("종료 날짜 (YYYY-MM-DD): ").strip()
            if lecture_dao.add_lecture(title, day, professor_id, start_time, end_time, start_date, end_date):
                print("✅ 강의 등록 완료")
            else:
                print("❌ 강의 등록 실패")

        elif choice == "3":
            user_id = input("사용자 ID: ").strip()
            lecture_id = input("강의 ID: ").strip()
            if enrollment_dao.add_enrollment(user_id, lecture_id):
                print("✅ 수강 신청 완료")
            else:
                print("❌ 수강 신청 실패")

        elif choice == "4":
            user_id = input("등록할 사용자 ID: ").strip()
            mac_address = input("블루투스 MAC 주소: ").strip()
            device_name = input("블루투스 장치 이름: ").strip()
            if bluetooth_dao.add_bluetooth_device(user_id, mac_address, device_name):
                print(f"✅ 블루투스 장치 추가 완료: {device_name} ({mac_address})")
            else:
                print("❌ 블루투스 장치 추가 실패")

        elif choice == "5":
            user_id = input("지문 등록할 사용자 ID: ").strip()
            fingerprint_data = scan_fingerprint()

            # 👇 여기에 암호화 적용
            encrypted_data = aes_cipher.encrypt(fingerprint_data)

            if fingerprint_dao.add_fingerprint(user_id, encrypted_data):
                print("✅ 지문 등록 완료 (암호화됨)")
            else:
                print("❌ 지문 등록 실패")

        elif choice == "0":
            print("프로그램을 종료합니다.")
            break

        else:
            print("❌ 잘못된 입력입니다. 다시 시도하세요.")

if __name__ == "__main__":
    main()

