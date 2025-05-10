from bluetooth import *
from fingerprint import register_fingerprint, verify_fingerprint
from user import add_user
from lecture import add_lecture
from enrollment import add_enrollment, get_enrolled_user_ids
from attendance import add_attendance
from db import initialize_database
import time

def main():
    initialize_database()

    while True:
        print("\n===== 메인 메뉴 =====")
        print("1. 사용자 등록")
        print("2. 강의 등록")
        print("3. 수강 신청")
        print("4. 블루투스 장치 수동 추가")
        print("5. 지문 등록")
        print("6. 블루투스 페어링")
        print("7. 강의를 시작합니까?")
        print("0. 종료")

        choice = input("선택 (0-7): ").strip()

        if choice == "1":
            student_id = input("학번 입력: ").strip()
            name = input("이름 입력: ").strip()
            major = input("전공 입력: ").strip()
            roles = {
                '1': '강의자',
                '2': '수강생'
            }
            role = None

            while role is None:
                num = input("1번: 강의자, 2번: 수강생\n번호를 입력하세요: ")
                role = roles.get(num)
                if role:
                    print(f"선택한 역할: {role}")
                else:
                    print(f"잘못된 입력입니다. 다시 선택해주세요.\n")
            if add_user(student_id, name, major, role.strip()):
                print("✅ 사용자 등록 완료")
            else:
                print("❌ 사용자 등록 실패")

        elif choice == "2":
            title = input("강의명: ").strip()
            day = input("요일 (월~금): ").strip()
            lecturer_id = input("강의자 아이디: ").strip()
            start_time = input("시작 시간 (HH:MM:SS): ").strip()
            end_time = input("종료 시간 (HH:MM:SS): ").strip()
            start_date = input("시작 날짜 (YYYY-MM-DD): ").strip()
            end_date = input("종료 날짜 (YYYY-MM-DD): ").strip()
            if add_lecture(title, day, lecturer_id, start_time, end_time, start_date, end_date):
                print("✅ 강의 등록 완료")
            else:
                print("❌ 강의 등록 실패")

        elif choice == "3":
            user_id = input("사용자 ID: ").strip()
            lecture_id = input("강의 ID: ").strip()
            if add_enrollment(user_id, lecture_id):
                print("✅ 수강 신청 완료")
            else:
                print("❌ 수강 신청 실패")

        elif choice == "4":
            user_id = input("등록할 사용자 ID: ").strip()
            mac_address = input("블루투스 MAC 주소: ").strip()
            name = input("블루투스 장치 이름: ").strip()
            if add_device(user_id, mac_address, name):
                print(f"✅ 블루투스 장치 추가 완료: {name} ({mac_address})")
            else:
                print("❌ 블루투스 장치 추가 실패")

        elif choice == "5":
            user_id = input("지문 등록할 사용자 ID: ").strip()
            if register_fingerprint(user_id):
                print("✅ 지문 등록 완료")
            else:
                print("❌ 지문 등록 실패")

        elif choice == "6":
            mac_addr = input("페어링 할 맥 주소: ")
            pair_device(mac_addr)

        elif choice == "7":
            lecture_id = input("출석 처리할 강의 ID: ").strip()
	    lecturer_id = get_lecturer_id_by_lecture_id(lecture_id)
	    mac_addr = get_mac_address_by_user_id(lecturer_id) # 강의자 기기의 맥 주소 가져옴
            print("블루투스가 연결되면 강의를 시작합니다...\n")

            # 강의자의 휴대폰에 10초 동안 블루투스 연결 시도
            start_time = time.time()
            connected = False
            while time.time() - start_time < 10:
                if is_connected(mac_addr):
                    connected = True
                    break
                time.sleep(1)  # 1초마다 체크

            # 연결에 실패하여 강의를 시작하지 못함
            if not connected:
                print("⏰ 10초 내에 연결되지 않았습니다. 강의를 시작할 수 없습니다.\n")

            # 연결에 성공하여 강의가 시작됨
            print("✍️ 강의를 시작합니다. 모두 자리에 착석해주세요!")
            misbehaving_students = set() # 블루투스 출석에 실패한 학생들의 아이디 집합(중복값을 제거하기 위함)
            enrolled_users = get_enrolled_user_ids(lecture_id) # 해당 강의를 신청한 학생 리스트
            user_mac_map = get_mac_addresses_by_user_ids(enrolled_users) # 학생들의 맥 주소 리스트

            try:
                while connected:
                    if not is_connected(mac_addr): # 강의자의 블루투스 연결이 끊어졌을 때 
                	print(f"🔨 {mac_addr} 연결이 끊어졌습니다. 강의를 종료하시려면 0을, 다시 시작하시려면 1을 눌러주세요.")
			user_input = input("입력: ").strip()
			    
		    if user_input == "0": # 강의를 완전히 종료 
		        print("강의를 종료합니다.")
		        break
			
		    elif user_input == "1": # 블루투스가 재연결되면 강의 다시 시작
		        print("🔄 블루투스 재연결을 시도합니다. 다시 강의를 시작합니다.")
		        start_time = time.time()
		        reconnected = False
		
		        while time.time() - start_time < 10:
		            if is_connected(mac_addr):
		                reconnected = True
		                break
		            time.sleep(1)
		
		        if not reconnected:
		            print("❌ 재연결 실패. 강의를 종료합니다.")
		            break
		        else:
		            connected = True  # 다시 루프 지속
		            continue
				
                    else: # 강의자의 블루투스 연결이 지속되어 블루투스 출석을 반복함
                        print("========= 블루투스 기기 스캔 시작 =========")
                        scanned_devices = scan_bluetooth_devices() # 스캔한 디바이스 리스트
                        print(scanned_devices)

                        for user_id in enrolled_users:
                            mac = user_mac_map.get(user_id) # 학생 아이디로 맥 주소를 가져옴
                            if mac in scanned_devices:
                                result = add_attendance(user_id, lecture_id, method="Bluetooth", status="1차출석완료")
                                print(f"✅ 사용자 {user_id} 출석 처리됨") if result else print(f"❌ 사용자 {user_id} 출석 실패")
                            else:
                                result = add_attendance(user_id, lecture_id, method="Bluetooth", status="1차출석실패")
                                print(f"❌ 사용자 {user_id} 결석 처리됨") if result else print(f"⚠️ 사용자 {user_id} 결석 기록 실패")
                                misbehaving_students.add(user_id)
                    time.sleep(10)  # 10초마다 체크
            except KeyboardInterrupt:
                print("\n모니터링을 수동으로 종료했습니다.")

            print(f"블루투스 출석을 실패한 학생들! 😡 지문 출석을 하세요!")
            misbehaving_students_list = list(misbehaving_students) # 집합을 리스트로 변환
            print(f"블루투스 출석에 실패한 학생들: {misbehaving_students_list}\n")

            # 블루투스 출석에 실패한 학생들의 지문 인식 출석 시작
            enrolled_users = get_enrolled_user_ids(lecture_id)

            for user_id in misbehaving_students_list:
                if user_id not in enrolled_users:
                    print(f"❌ 사용자 {user_id}는 이 강의에 수강 신청되어 있지 않습니다.")
                    return 
                print(f"{user_id}번 학생의 지문 인식을 시작합니다...")
                if verify_fingerprint(user_id):
                    if add_attendance(user_id, lecture_id, method="Both", status="2차출석완료"):
                        print(f"✅ 사용자 {user_id}의 출석 처리 완료")
                    else:
                        print(f"❌ 사용자 {user_id}의 출석 기록 실패")
                else:
                    add_attendance(user_id, lecture_id, method="Fingerprint", status="2차출석실패")
                    print(f"❌ 사용자 {user_id} 지문 인증 실패 (출석 실패 처리됨)")

            # 인증하지 않은 학생들 처리
            not_verified_users = [user_id for user_id in enrolled_users if user_id not in misbehaving_students]
            for user_id in not_verified_users:
                add_attendance(user_id, lecture_id, method="Fingerprint", status="2차출석제외")
                print(f"⚠️ 사용자 {user_id}는 지문 인증 대상이 아니므로 2차출석제외 처리됨")

        elif choice == "0":
	            print("프로그램을 종료합니다.")
	            break

        else:
            print("❌ 잘못된 입력입니다. 다시 시도하세요.")

if __name__ == "__main__":
    main()

