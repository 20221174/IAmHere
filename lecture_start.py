from config.config import AES_KEY
from db import *
from bluetooth import *
from fingerprint import *
from notifier import *
import time
from AES256 import *
def main():
    initialize_database()

    # DAO 객체 생성
    user_dao = UserDAO()
    bluetooth_dao = BluetoothDeviceDAO()
    attendance_dao = AttendanceDAO()
    enrollment_dao = EnrollmentDAO()
    lecture_dao = LectureDAO()
    fingerprint_dao = FingerprintDAO()

    
    # AES56 객체 생성
    aes_cipher = AES256(AES_KEY)
    
    while True:
        print("\n===== 메인 메뉴 =====")
        print("6. 블루투스 페어링")
        print("7. 강의를 시작합니까?")
        print("0. 종료")

        choice = input("선택 (0-7): ").strip()

        if choice == "6":
            mac_addr = input("페어링 할 맥 주소: ")
            pair_device(mac_addr)

        elif choice == "7":
            lecture_id = input("출석 처리할 강의 ID: ").strip()
            lecture_data = lecture_dao.get_lecture_by_id(lecture_id)
            print(lecture_data)
            professor_id = lecture_data['professor_id']
            lecture_title = lecture_data['title']
            mac_addr = (bluetooth_dao.get_mac_by_user_id(professor_id) or {}).get('mac_address')
            print("블루투스가 연결되면 강의를 시작합니다...\n")

            start_time = time.time()
            connected = False

            while time.time() - start_time < 10:
                if is_connected(mac_addr):
                    connected = True
                    break
                time.sleep(1)

            if not connected:
                print("⏰ 10초 내에 연결되지 않았습니다. 강의를 시작할 수 없습니다.\n")
                continue

            print("✍️ 강의를 시작합니다. 모두 자리에 착석해주세요!")
            misbehaving_students = set()

            # 강의 수강자 ID 리스트
            enrolled_dict = (enrollment_dao.get_enrollments_by_lecture(lecture_id) or {})
            enrolled_users = [entry['user_id'] for entry in enrolled_dict]
            print(enrolled_users)

            # 수강자별 MAC 주소 딕셔너리
            user_mac_map = bluetooth_dao.get_mac_addresses_by_user_ids(enrolled_users)

            try:
                while connected:
                    if not is_connected(mac_addr):
                        print(f"🔨 {mac_addr} 연결이 끊어졌습니다. 강의를 종료합니다.")
                        break
                    else:
                        print("========= 블루투스 기기 스캔 시작 =========")
                        scanned_devices = scan_bluetooth_devices()
                        print(scanned_devices)

                        for user_id in enrolled_users:
                            mac = user_mac_map.get(user_id)
                            if mac in scanned_devices:
                                result = attendance_dao.add_attendance(
                                    user_id, lecture_id, method="Bluetooth", status="1차출석완료"
                                )
                                print(f"✅ 사용자 {user_id} 출석 처리됨") if result else print(f"❌ 사용자 {user_id} 출석 실패")
                            else:
                                result = attendance_dao.add_attendance(
                                    user_id, lecture_id, method="Bluetooth", status="1차출석실패"
                                )
                                print(f"❌ 사용자 {user_id} 결석 처리됨") if result else print(f"⚠️ 사용자 {user_id} 결석 기록 실패")
                                misbehaving_students.add(user_id)
                    time.sleep(10)
            except KeyboardInterrupt:
                print("\n모니터링을 수동으로 종료했습니다.")

            print(f"블루투스 출석을 실패한 학생들! 😡 지문 출석을 하세요!")
            misbehaving_students_list = list(misbehaving_students)



            print(f"블루투스 출석에 실패한 학생들: {misbehaving_students_list}\n")

            for user_id in misbehaving_students_list:
                if user_id not in enrolled_users:
                    print(f"❌ 사용자 {user_id}는 이 강의에 수강 신청되어 있지 않습니다.")
                    return

                print(f"{user_id}번 학생의 지문 인식을 시작합니다...")

                user_data = user_dao.get_user_by_id(user_id)
                student_name = user_data['name']
                send_check(student_name, lecture_title)

                fingerprint_data = fingerprint_dao.get_fingerprint_by_user_id(user_id)

                if fingerprint_data is not None:
                    encrypted_fingerprint_data = fingerprint_data['fingerprint_template']  # 암호화된 문자열 필드 이름이 'fingerprint' 라고 가정
                    decrypted_fingerprint_data = aes_cipher.decrypt(encrypted_fingerprint_data)  # 복호화
                else:
                    print("지문 데이터가 없습니다.")

                fingerprint_data['fingerprint_template'] = decrypted_fingerprint_data

                max_attempts = 3
                success = False

                for attempt in range(1, max_attempts + 1):
                    print(f"🔁 지문 인증 시도 {attempt}/{max_attempts}")
                    
                    if verify_fingerprint(fingerprint_data): # 지문 인식 성공 시 
                        if attendance_dao.add_attendance(user_id, lecture_id, method="Both", status="2차출석완료"):
                            print(f"✅ 사용자 {user_id}의 출석 처리 완료")
                        else:
                            print(f"❌ 사용자 {user_id}의 출석 기록 실패")
                        success = True
                        send_result(student_name, success)
                        break
                    else: # 지문 인식 실패 시
                        print(f"❌ 지문 인증 실패 (시도 {attempt})")
                        send_result(student_name, success)

                if not success:
                    attendance_dao.add_attendance(user_id, lecture_id, method="Fingerprint", status="2차출석실패")
                    print(f"❌ 사용자 {user_id} 지문 인증 3회 실패 (출석 실패 처리됨)")

            # 지문 인식 출석에 제외된 학생들 처리
            not_verified_users = [user_id for user_id in enrolled_users if user_id not in misbehaving_students]
            for user_id in not_verified_users:
                attendance_dao.add_attendance(user_id, lecture_id, method="Fingerprint", status="2차출석제외")
                print(f"⚠️ 사용자 {user_id}는 지문 인증 대상이 아니므로 2차출석제외 처리됨")

        elif choice == "9":
            send_check("test", "test")
            send_result("test", True)
        elif choice == "0":
            print("프로그램을 종료합니다.")
            break

        else:
            print("❌ 잘못된 입력입니다. 다시 시도하세요.")


if __name__ == "__main__":
    main()

