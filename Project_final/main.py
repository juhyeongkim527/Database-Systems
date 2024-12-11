import pymysql as pms
import os
import datetime
import threading
import time
import queue

# Connect to the database
db = pms.connect(
    host='localhost',
    port=3306,
    user='root',
    password=os.environ['MYSQL_PASSWORD'],
    db='music_streaming_service',
    charset='utf8mb4',
)

cursor = db.cursor()

pre_admin_password = 'admin'  # 관리자 사전 인증 비밀번호
admin_roles_list = ['music_manager', 'user_manager', 'system_manager']
genre_list = ['ballad', 'kpop', 'pop', 'rnb', 'dance', 'hiphop', 'rock', 'jazz', 'classic', 'etc']


def login_menu():
    global pre_admin_password
    print()
    print("=============================================")
    print("|                로그인 메뉴                |")
    print("=============================================")
    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()
    print("1. 사용자 로그인")
    print("2. 관리자 로그인")
    print("3. 사용자 회원가입")
    print("4. 관리자 회원가입")
    print("5. 종료")
    print()
    choice = input("선택(1~5) : ")

    if choice == '1':
        sign_in_user()
    elif choice == '2':
        sign_in_admin()
    elif choice == '3':
        sign_up_user()
    elif choice == '4':
        if (pre_admin_password == input("관리자 사전 인증 비밀번호를 입력하세요 : ")):
            sign_up_admin()
        else:
            print("사전 인증 비밀번호가 틀렸습니다. 다시 시도해주세요.")
            login_menu()
    elif choice == '5':
        print("안녕히 가세요 !")
        exit()
    else:
        print()
        print("잘못된 선택입니다. 다시 시도해주세요.")
        login_menu()


def sign_up_user():
    print()
    print("=============================================")
    print("|              사용자 회원가입 메뉴            |")
    print("=============================================")
    print()

    while (1):
        uid = input("아이디를 입력하세요(최대 15자) : ")
        if (uid == '' or len(uid) > 15):
            print("아이디를 다시 입력하세요.")
            print()
        else:
            sql = "SELECT * FROM user WHERE uid = %s"
            cursor.execute(sql, (uid))
            result = cursor.fetchall()
            cursor.connection.commit()
            if (len(result) != 0):
                print("중복된 아이디입니다. 다른 아이디를 입력하세요.")
                print()
            else:
                break

    while (1):
        print()
        upw = input("비밀번호를 입력하세요(최대 20자) : ")
        if (upw == '' or len(upw) > 20):
            print("비밀번호를 다시 입력하세요.")
            print()
        else:
            break

    while (1):
        print()
        name = input("이름을 입력하세요(최대 30자) : ")
        if (name == '' or len(name) > 30):
            print("이름을 다시 입력하세요.")
            print()
        else:
            break

    while (1):
        print()
        email = input("이메일을 입력하세요(최대 50자) : ")
        if (email == '' or len(email) > 50):
            print("이메일을 다시 입력하세요.")
            print()
        else:
            break
    sign_up_date = datetime.datetime.now().strftime("%Y-%m-%d")

    while (1):
        print()
        birth_date = input("생년월일을 입력하세요(YYYY-MM-DD) : ")
        try:
            datetime.datetime.strptime(birth_date, "%Y-%m-%d")
            break
        except ValueError:
            print("잘못된 형식의 생년월일입니다. 다시 입력하세요.")
            print()

    while (1):
        print()
        gender = input("성별을 입력하세요('M' 또는 'F') : ")
        gender = gender.upper()
        if (gender == 'M' or gender == 'F'):
            break
        else:
            print("잘못된 성별입니다. 다시 입력하세요.")
            print()

    sql = "INSERT INTO user (uid, upw, name, email, sign_up_date, birth_date, gender) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (uid, upw, name, email, sign_up_date, birth_date, gender))
    cursor.connection.commit()

    print()
    print("회원가입 성공 !")
    print("다시 로그인 해주세요 !")
    print()
    login_menu()


def sign_up_admin():
    print()
    print("=============================================")
    print("|              관리자 회원가입 메뉴            |")
    print("=============================================")
    print()

    while (1):
        aid = input("ID를 입력하세요(최대 15자) : ")
        if (aid == '' or len(aid) > 15):
            print("ID를 다시 입력하세요.")
            print()
        else:
            sql = "SELECT * FROM admin WHERE aid = %s"
            cursor.execute(sql, (aid))
            result = cursor.fetchall()
            cursor.connection.commit()
            if (len(result) != 0):
                print("중복된 ID입니다. 다른 ID를 입력하세요.")
                print()
            else:
                break

    while (1):
        apw = input("비밀번호를 입력하세요(최대 20자) : ")
        if (apw == '' or len(apw) > 20):
            print("비밀번호를 다시 입력하세요.")
            print()
        else:
            break

    while (1):
        name = input("이름을 입력하세요(최대 30자) : ")
        if (name == '' or len(name) > 30):
            print("이름을 다시 입력하세요.")
            print()
        else:
            break

    while (1):
        email = input("이메일을 입력하세요(최대 50자) : ")
        if (email == '' or len(email) > 50):
            print("이메일을 다시 입력하세요.")
            print()
        else:
            break

    adm_roles = []
    while (1):
        role = input("당신의 관리자 역할을 입력하세요('M' : 음악 관리자, 'U' : 사용자 관리자, 'S' : 시스템 관리자, 'DONE' : 입력 완료) : ")
        role = role.upper()
        if role == 'DONE':
            if (len(adm_roles) == 0):
                print("하나 이상의 역할을 입력하세요.")
                print()
            else:
                break
        elif (role in ['M', 'U', 'S']):
            if (role in adm_roles):
                print("이미 입력한 역할입니다. 다시 입력하세요.")
                print()
            else:
                adm_roles.append(role)
        else:
            print("잘못된 역할입니다. 다시 입력하세요.")
            print()

    sql = "INSERT INTO admin (aid, apw, name, email) VALUES (%s, %s, %s, %s)"
    cursor.execute(sql, (aid, apw, name, email))

    adm_id = cursor.lastrowid  # Insert한 admin의 id를 가져오기

    sql = "INSERT INTO admin_role (adm_id, adm_role) VALUES (%s, %s)"
    for role in adm_roles:
        if (role == 'M'):
            cursor.execute(sql, (adm_id, admin_roles_list[0]))
        elif (role == 'U'):
            cursor.execute(sql, (adm_id, admin_roles_list[1]))
        elif (role == 'S'):
            cursor.execute(sql, (adm_id, admin_roles_list[2]))

    cursor.connection.commit()

    print()
    print("회원가입 성공 !")
    print("다시 로그인 해주세요 !")
    print()
    login_menu()


def sign_in_user():
    print()
    print("=============================================")
    print("|              사용자 로그인 메뉴             |")
    print("=============================================")
    print()

    while (1):
        uid = input("ID를 입력하세요 : ")
        if (uid == ''):
            print("ID를 다시 입력하세요.")
            print()
        else:
            break
    while (1):
        upw = input("비밀번호를 입력하세요 : ")
        if (upw == ''):
            print("비밀번호를 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM user WHERE uid = %s AND upw = %s"
    cursor.execute(sql, (uid, upw))
    result = cursor.fetchall()
    cursor.connection.commit()

    if (len(result) == 0):
        print()
        print("ID 또는 비밀번호가 잘못되었습니다. 다시 시도해주세요.")
        print()
        login_menu()
    else:
        print()
        print("로그인 성공 !")
        print()
        user_id = result[0][0]
        user_menu(user_id)


def sign_in_admin():
    print()
    print("=============================================")
    print("|             관리자 로그인 메뉴             |")
    print("=============================================")
    print()

    aid = input("ID를 입력하세요 : ")
    apw = input("비밀번호를 입력하세요 : ")

    sql = "SELECT * FROM admin WHERE aid = %s AND apw = %s"
    cursor.execute(sql, (aid, apw))
    result = cursor.fetchall()

    if (len(result) == 0):
        print()
        print("ID 또는 비밀번호가 잘못되었습니다. 다시 시도해주세요.")
        print()
        login_menu()
    else:
        print()
        print("로그인 성공 !")
        admin_id = result[0][0]
        admin_menu(admin_id)


def user_menu(id):
    print()
    print("=============================================")
    print("|                 사용자 메뉴               |")
    print("=============================================")
    print()
    sql = "SELECT * FROM user WHERE id = %s"
    cursor.execute(sql, (id))
    result = cursor.fetchall()
    print(f"안녕하세요, {result[0][1]}님 !")
    print()
    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()

    print("1. 음악 검색")
    print("2. 아티스트 검색")
    print("3. 사용자 검색")
    print("4. Top 10 가장 많이 들은 음악 보기")
    print("5. Top 10 가장 좋아요를 많이 받은 음악 보기")
    print("6. 음악 듣기")
    print("7. 내 플레이리스트")
    print("8. 다른 사용자의 플레이리스트 공유하기")
    print("9. 좋아요 누른 음악 보기")
    print("10. 내 정보 수정")
    print("11. 로그아웃")
    print("12. 계정 삭제")
    print("13. 종료")
    print()

    choice = input("선택(1~13) : ")

    if (choice == '1'):
        search_music(id)
    elif (choice == '2'):
        search_artist(id)
    elif (choice == '3'):
        search_user(id)
    elif (choice == '4'):
        show_top_10_music(id, 'play_count')
    elif (choice == '5'):
        show_top_10_music(id, 'like_count')
    elif (choice == '6'):
        play_music(id)
    elif (choice == '7'):
        my_playlist(id)
    elif (choice == '8'):
        share_playlist(id)
    elif (choice == '9'):
        show_liked_music(id)
    elif (choice == '10'):
        edit_user_info(id)
    elif (choice == '11'):
        print("로그아웃 되었습니다.")
        login_menu()
    elif (choice == '12'):
        choice = input("정말로 계정을 삭제하시겠습니까? (Y/N) : ")
        choice = choice.upper()
        if (choice == 'Y'):
            sql = "DELETE FROM user WHERE id = %s"
            cursor.execute(sql, (id))
            cursor.connection.commit()
            print("계정이 삭제되었습니다. 로그인 화면으로 돌아갑니다.")
            login_menu()
        elif (choice == 'N'):
            user_menu(id)
    elif (choice == '13'):
        print("안녕히 가세요 !")
        exit()
    else:
        print("잘못된 선택입니다. 다시 시도해주세요.")
        user_menu(id)


def show_liked_music(id):
    print()
    print("=============================================")
    print("|            좋아요 누른 음악 보기           |")
    print("=============================================")
    print()

    sql = "SELECT * FROM like_music WHERE usr_id = %s"
    cursor.execute(sql, (id))
    result = cursor.fetchall()

    if (len(result) == 0):
        print("좋아요를 누른 음악이 없습니다.")
        print()
        user_menu(id)
    else:
        for music in result:
            sql = "SELECT * FROM music WHERE id = %s"
            cursor.execute(sql, (music[1]))
            result_ = cursor.fetchall()
            print(f"음악 제목 : {result_[0][2]}")
            print(f"좋아요 누른 날짜 : {music[2]}")
            print()
        user_menu(id)


def edit_user_info(id):
    print()
    print("=============================================")
    print("|              사용자 정보 수정 메뉴          |")
    print("=============================================")
    print()

    sql = "SELECT * FROM user WHERE id = %s"
    cursor.execute(sql, (id))
    result = cursor.fetchall()

    print(f"아이디 : {result[0][4]}")
    print(f"비밀번호 : {result[0][5]}")
    print(f"이름 : {result[0][1]}")
    print(f"현재 이메일 : {result[0][2]}")
    print(f"가입 날짜 : {result[0][3]}")
    print(f"생년월일 : {result[0][6]}")
    if (result[0][7] == 'M'):
        print("성별 : 남성")
    else:
        print("성별 : 여성")
    print()

    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()
    print("1. 아이디 변경")
    print("2. 비밀번호 변경")
    print("3. 이름 변경")
    print("4. 이메일 변경")
    print("5. 생년월일 변경")
    print("6. 성별 변경")
    print("7. 사용자 메뉴로 돌아가기")
    print()

    choice = input("선택(1~7) : ")

    if (choice == '1'):
        while (1):
            uid = input("변경할 아이디를 입력하세요(최대 15자) : ")
            if (uid == '' or len(uid) > 15):
                print("아이디를 다시 입력하세요.")
                print()
            else:
                break

        sql = "UPDATE user SET uid = %s WHERE id = %s"
        cursor.execute(sql, (uid, id))
        cursor.connection.commit()
        print("아이디 변경 성공 !")
        edit_user_info(id)

    elif (choice == '2'):
        while (1):
            upw = input("변경할 비밀번호를 입력하세요(최대 20자) : ")
            if (upw == '' or len(upw) > 20):
                print("비밀번호를 다시 입력하세요.")
                print()
            else:
                break

        sql = "UPDATE user SET upw = %s WHERE id = %s"
        cursor.execute(sql, (upw, id))
        cursor.connection.commit()
        print("비밀번호 변경 성공 !")
        edit_user_info(id)

    elif (choice == '3'):
        while (1):
            name = input("변경할 이름을 입력하세요(최대 30자) : ")
            if (name == '' or len(name) > 30):
                print("이름을 다시 입력하세요.")
                print()
            else:
                break

        sql = "UPDATE user SET name = %s WHERE id = %s"
        cursor.execute(sql, (name, id))
        cursor.connection.commit()
        print("이름 변경 성공 !")
        edit_user_info(id)

    elif (choice == '4'):
        while (1):
            email = input("변경할 이메일을 입력하세요(최대 50자) : ")
            if (email == '' or len(email) > 50):
                print("이메일을 다시 입력하세요.")
                print()
            else:
                break

        sql = "UPDATE user SET email = %s WHERE id = %s"
        cursor.execute(sql, (email, id))
        cursor.connection.commit()
        print("이메일 변경 성공 !")
        edit_user_info(id)

    elif (choice == '5'):
        while (1):
            birth_date = input("변경할 생년월일을 입력하세요(YYYY-MM-DD) : ")
            try:
                datetime.datetime.strptime(birth_date, "%Y-%m-%d")
                break
            except ValueError:
                print("잘못된 형식의 생년월일입니다. 다시 입력하세요.")
                print()

        sql = "UPDATE user SET birth_date = %s WHERE id = %s"
        cursor.execute(sql, (birth_date, id))
        cursor.connection.commit()
        print("생년월일 변경 성공 !")
        edit_user_info(id)

    elif (choice == '6'):
        while (1):
            gender = input("변경할 성별을 입력하세요('M' 또는 'F') : ")
            if (gender in ['M', 'F']):
                break
            else:
                print("잘못된 성별입니다. 다시 입력하세요.")

        sql = "UPDATE user SET gender = %s WHERE id = %s"
        cursor.execute(sql, (gender, id))
        cursor.connection.commit()
        print("성별 변경 성공 !")
        edit_user_info(id)

    elif (choice == '7'):
        user_menu(id)

    else:
        print("잘못된 선택입니다. 다시 시도해주세요.")
        edit_user_info(id)


def share_playlist(id):
    print()
    print("=============================================")
    print("|        다른 사용자의 플레이리스트 공유하기       |")
    print("=============================================")
    print()

    while (1):
        usr_id = input("플레이리스트를 가진 사용자의 id를 입력하세요 : ")
        if (usr_id == ''):
            print("id를 다시 입력하세요.")
            print()
        else:
            break

    sql = 'SELECT * FROM user WHERE id = %s'
    cursor.execute(sql, (usr_id))
    result = cursor.fetchall()

    if (len(result) == 0):
        print("해당 id의 사용자가 존재하지 않습니다. 메뉴로 돌아갑니다.")
        print()
        user_menu(id)

    else:
        print()
        print(f"<\"{result[0][1]}\"님이 생성한 플레이리스트 목록>")
        user_name = result[0][1]
        sql = 'SELECT * FROM play_list WHERE create_usr_id = %s'
        cursor.execute(sql, (usr_id))
        result = cursor.fetchall()

        if (len(result) == 0):
            print("해당 사용자가 생성한 플레이리스트가 없습니다.")
            print()
        else:
            is_print = False
            for play_list in result:
                if (play_list[4] == 'A'):  # view_access
                    is_print = True
                    print(f"플레이리스트 id : {play_list[0]}")
                    print(f"플레이리스트 이름 : {play_list[2]}")
                    print(f"생성 날짜 : {play_list[3]}")
                    if (play_list[5] == 'A'):
                        print(f"공유 권한 : 허용")
                    else:
                        print(f"공유 권한 : 거부")

                    sql = "SELECT * FROM play_list_music WHERE pl_id = %s"
                    cursor.execute(sql, (play_list[0]))
                    result_ = cursor.fetchall()
                    print(f"음악 개수 : {len(result_)}")
                    for music in result_:
                        sql = "SELECT * FROM music WHERE id = %s"
                        cursor.execute(sql, (music[1]))
                        result__ = cursor.fetchall()
                        print(f"음악 제목 : {result__[0][2]}")
                    print()
            if (is_print == False):
                print("해당 사용자가 생성한 모든 플레이리스트는 비공개 상태입니다.")
                print()

        print(f"<\"{user_name}\"님이 공유한 플레이리스트 목록>")
        sql = "SELECT * FROM play_list_share WHERE usr_id = %s"
        cursor.execute(sql, (usr_id))
        result = cursor.fetchall()

        if (len(result) == 0):
            print("해당 사용자가 공유한 플레이리스트가 없습니다.")
            print()
        else:
            is_print = False
            for play_list in result:
                if (play_list[3] == 'A'):  # view_access
                    is_print = True
                    print(f"플레이리스트 id : {play_list[1]}")
                    sql = "SELECT * FROM play_list WHERE id = %s"
                    cursor.execute(sql, (play_list[1]))
                    result_ = cursor.fetchall()
                    print(f"플레이리스트 이름 : {result_[0][2]}")
                    print(f"공유 날짜 : {play_list[2]}")
                    if (result_[0][5] == 'A'):
                        print(f"공유 권한 : 허용")
                    else:
                        print(f"공유 권한 : 거부")
                    sql = "SELECT * FROM play_list_music WHERE pl_id = %s"
                    cursor.execute(sql, (play_list[1]))
                    result_ = cursor.fetchall()
                    print(f"음악 개수 : {len(result_)}")
                    for music in result_:
                        sql = "SELECT * FROM music WHERE id = %s"
                        cursor.execute(sql, (music[1]))
                        result__ = cursor.fetchall()
                        print(f"음악 제목 : {result__[0][2]}")
                    print()
            if (is_print == False):
                print("해당 사용자가 공유한 모든 플레이리스트는 비공개 상태입니다.")
                print()

    while (1):
        play_list_id = input("공유할 플레이리스트의 id를 입력하세요 : ")
        if (play_list_id == ''):
            print("id를 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM play_list WHERE id = %s"
    cursor.execute(sql, (play_list_id))
    result = cursor.fetchall()

    if (len(result) == 0):
        print("해당 id의 플레이리스트가 존재하지 않습니다. 메뉴로 돌아갑니다.")
        print()
        user_menu(id)
    else:
        if (result[0][1] == id):
            print("내가 생성한 플레이리스트입니다. 메뉴로 돌아갑니다.")
            print()
            user_menu(id)
        if (result[0][5] == 'D'):
            print("해당 플레이리스트는 공유가 거부된 상태입니다. 메뉴로 돌아갑니다.")
            print()
            user_menu(id)
        else:
            sql = "SELECT * FROM play_list_share WHERE usr_id = %s and pl_id = %s"
            cursor.execute(sql, (id, play_list_id))
            result = cursor.fetchall()

            if (len(result) != 0):
                print("이미 공유한 플레이리스트입니다. 메뉴로 돌아갑니다.")
                print()
                user_menu(id)
            else:
                sql = "INSERT INTO play_list_share (usr_id, pl_id, share_date, view_access) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (id, play_list_id, datetime.datetime.now().strftime("%Y-%m-%d"), 'A'))
                cursor.connection.commit()

                print("플레이리스트 공유 성공 !")
                print()
                user_menu(id)


def my_playlist(id):
    print()
    print("=============================================")
    print("|              나의 플레이리스트 메뉴          |")
    print("=============================================")
    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()

    print("1. 나의 플레이리스트 목록 보기")
    print("2. 플레이리스트 생성")
    print("3. 플레이리스트 권한 수정")
    print("4. 플레이리스트에 음악 추가")
    print("5. 플레이리스트에서 음악 삭제")
    print("6. 플레이리스트 삭제")
    print("7. 사용자 메뉴로 돌아가기")
    print()
    choice = input("선택(1~7) : ")

    if (choice == '1'):
        show_my_playlist(id)
    elif (choice == '2'):
        make_playlist(id)
    elif (choice == '3'):
        edit_access_of_playlist(id)
    elif (choice == '4'):
        add_music_to_playlist(id)
    elif (choice == '5'):
        delete_music_from_playlist(id)
    elif (choice == '6'):
        delete_playlist(id)
    elif (choice == '7'):
        user_menu(id)
    else:
        print("잘못된 선택입니다. 다시 시도해주세요.")
        my_playlist(id)


def delete_playlist(id):
    print()
    print("=============================================")
    print("|              플레이리스트 삭제 메뉴          |")
    print("=============================================")
    print()

    while (1):
        play_list_id = input("삭제할 플레이리스트의 id를 입력하세요 : ")
        if (play_list_id == ''):
            print("id를 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM play_list WHERE id = %s and create_usr_id = %s"
    cursor.execute(sql, (play_list_id, id))
    result = cursor.fetchall()

    if (len(result) != 0):
        sql = "DELETE FROM play_list WHERE id = %s"
        cursor.execute(sql, (play_list_id))
        cursor.connection.commit()
        print("플레이리스트 삭제 성공 !")
        my_playlist(id)

    else:
        sql = "SELECT * FROM play_list_share WHERE usr_id = %s and pl_id = %s"
        cursor.execute(sql, (id, play_list_id))
        result = cursor.fetchall()

        if (len(result) != 0):
            sql = "DELETE FROM play_list_share WHERE usr_id = %s and pl_id = %s"
            cursor.execute(sql, (id, play_list_id))
            cursor.connection.commit()
            print("플레이리스트 삭제 성공 !")
            my_playlist(id)
        else:
            print("나에게 존재하지 않는 플레이리스트입니다. 메뉴로 돌아갑니다.")
            my_playlist(id)


def show_my_playlist(id):
    print()
    print("=============================================")
    print("|              나의 플레이리스트 목록          |")
    print("=============================================")
    print()

    # play_list that user created
    sql = "SELECT * FROM play_list WHERE create_usr_id = %s"
    cursor.execute(sql, (id))
    result = cursor.fetchall()

    print("<내가 생성한 플레이리스트>")
    if (len(result) == 0):
        print("생성한 플레이리스트가 없습니다.")
        print()
    else:
        for play_list in result:
            print(f"플레이리스트 id : {play_list[0]}")
            print(f"플레이리스트 이름 : {play_list[2]}")
            print(f"생성 날짜 : {play_list[3]}")
            if (play_list[4] == 'A'):
                print(f"조회 권한 : 허용")
            else:
                print(f"조회 권한 : 거부")
            if (play_list[5] == 'A'):
                print(f"공유 권한 : 허용")
            else:
                print(f"공유 권한 : 거부")
            sql = "SELECT * FROM play_list_music WHERE pl_id = %s"
            cursor.execute(sql, (play_list[0]))
            result_ = cursor.fetchall()
            print(f"음악 개수 : {len(result_)}")
            for music in result_:
                sql = "SELECT * FROM music WHERE id = %s"
                cursor.execute(sql, (music[1]))
                result__ = cursor.fetchall()
                print(f"음악 제목 : {result__[0][2]}")
            print()

    sql = "SELECT * FROM play_list_share WHERE usr_id = %s"
    cursor.execute(sql, (id))
    result = cursor.fetchall()

    if (len(result) == 0):
        print("공유한 플레이리스트가 없습니다.")
    else:
        print("<내가 공유한 플레이리스트>")
        for play_list in result:
            print(f"플레이리스트 id : {play_list[1]}")
            sql = "SELECT * FROM play_list WHERE id = %s"
            cursor.execute(sql, (play_list[1]))
            result_ = cursor.fetchall()
            print(f"플레이리스트 이름 : {result_[0][2]}")
            print(f"공유 날짜 : {play_list[2]}")
            if (play_list[3] == 'A'):
                print(f"조회 권한 : 허용")
            else:
                print(f"조회 권한 : 거부")
            sql = "SELECT * FROM play_list_music WHERE pl_id = %s"
            cursor.execute(sql, (play_list[1]))
            result_ = cursor.fetchall()
            print(f"음악 개수 : {len(result_)}")
            for music in result_:
                sql = "SELECT * FROM music WHERE id = %s"
                cursor.execute(sql, (music[1]))
                result__ = cursor.fetchall()
                print(f"음악 제목 : {result__[0][2]}")
            print()

    my_playlist(id)


def make_playlist(id):
    print()
    print("=============================================")
    print("|              플레이리스트 생성 메뉴          |")
    print("=============================================")
    print()

    while (1):
        name = input("플레이리스트 이름을 입력하세요(최대 30자) : ")
        if (name == '' or len(name) > 30):
            print("플레이리스트 이름을 다시 입력하세요.")
            print()
        else:
            break

    create_date = datetime.datetime.now().strftime("%Y-%m-%d")

    while (1):
        view_access = input("조회 권한을 입력하세요('A' : 허용, 'D' : 거부) : ")
        view_access = view_access.upper()
        if (view_access in ['A', 'D']):
            break
        else:
            print("조회 권한을 다시 입력하세요.")
            print()

    while (1):
        share_access = input("공유 권한을 입력하세요('A' : 허용, 'D' : 거부) : ")
        share_access = share_access.upper()
        if (share_access in ['A', 'D']):
            break
        else:
            print("공유 권한을 다시 입력하세요.")
            print()

    sql = "INSERT INTO play_list (create_usr_id, name, create_date, view_access, share_access) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql, (id, name, create_date, view_access, share_access))
    cursor.connection.commit()

    print()
    print("플레이리스트 생성 성공 !")
    my_playlist(id)


def edit_access_of_playlist(id):
    print()
    print("=============================================")
    print("|            플레이리스트 권한 수정 메뉴        |")
    print("=============================================")
    print()

    while (1):
        play_list_id = input("권한을 수정할 플레이리스트의 id를 입력하세요 : ")
        if (play_list_id == ''):
            print("id를 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM play_list WHERE id = %s and create_usr_id = %s"
    cursor.execute(sql, (play_list_id, id))
    result = cursor.fetchall()

    if (len(result) != 0):
        print()
        print(f"플레이리스트 이름 : {result[0][2]}")
        if (result[0][4] == 'A'):
            print(f"현재 조회 권한 : 허용")
        else:
            print(f"현재 조회 권한 : 거부")
        if (result[0][5] == 'A'):
            print(f"현재 공유 권한 : 허용")
        else:
            print(f"현재 공유 권한 : 거부")
        print()

        while (1):
            view_access = input("조회 권한을 입력하세요('A' : 허용, 'D' : 거부) : ")
            view_access = view_access.upper()
            if (view_access in ['A', 'D']):
                break
            else:
                print("조회 권한을 다시 입력하세요.")
                print()

        while (1):
            share_access = input("공유 권한을 입력하세요('A' : 허용, 'D' : 거부) : ")
            share_access = share_access.upper()
            if (share_access in ['A', 'D']):
                break
            else:
                print("공유 권한을 다시 입력하세요.")
                print()

        sql = "UPDATE play_list SET view_access = %s, share_access = %s WHERE id = %s"
        cursor.execute(sql, (view_access, share_access, play_list_id))
        cursor.connection.commit()

    else:
        sql = "SELECT * FROM play_list_share WHERE usr_id = %s and pl_id = %s"
        cursor.execute(sql, (id, play_list_id))
        result = cursor.fetchall()

        if (len(result) == 0):
            print("나에게 해당 id의 플레이리스트가 존재하지 않습니다. 메뉴로 돌아갑니다.")
            my_playlist(id)
        else:
            print()
            print(f"플레이리스트 이름 : {result[0][1]}")
            if (result[0][3] == 'A'):
                print(f"현재 조회 권한 : 허용")
            else:
                print(f"현재 조회 권한 : 거부")
            print()

            while (1):
                view_access = input("조회 권한을 입력하세요('A' : 허용, 'D' : 거부) : ")
                view_access = view_access.upper()
                if (view_access in ['A', 'D']):
                    break
                else:
                    print("조회 권한을 다시 입력하세요.")
                    print()

            sql = "UPDATE play_list_share SET view_access = %s WHERE usr_id = %s and pl_id = %s"
            cursor.execute(sql, (view_access, id, play_list_id))
            cursor.connection.commit()

    print()
    print("플레이리스트 권한 수정 성공 !")
    my_playlist(id)


def add_music_to_playlist(id):
    print()
    print("=============================================")
    print("|           플레이리스트에 음악 추가하기         |")
    print("=============================================")
    print()

    while (1):
        play_list_id = input("음악을 추가할 플레이리스트의 id를 입력하세요 : ")
        if (play_list_id == ''):
            print("id를 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM play_list WHERE id = %s and create_usr_id = %s"
    cursor.execute(sql, (play_list_id, id))
    result = cursor.fetchall()

    if (len(result) != 0):
        print()
        print(f"플레이리스트 이름 : {result[0][2]}")
        print(f"생성 날짜 : {result[0][3]}")
        print()

        while (1):
            title = input("추가할 음악의 제목을 입력하세요 : ")
            if (title == ''):
                print("제목을 다시 입력하세요.")
                print()
            else:
                break

        sql = "SELECT * FROM music WHERE name = %s"
        cursor.execute(sql, (title))
        result = cursor.fetchall()

        if (len(result) == 0):
            print(f"\"{title}\" 제목의 음악이 존재하지 않습니다. 다시 입력하세요.")
            my_playlist(id)
        else:
            mus_id = result[0][0]

            sql = "SELECT * FROM play_list_music WHERE mus_id = %s and pl_id = %s"
            cursor.execute(sql, (mus_id, play_list_id))
            result = cursor.fetchall()

        if (len(result) != 0):
            print()
            print("이미 플레이리스트에 추가된 음악입니다.")
        else:
            sql = "INSERT INTO play_list_music (mus_id, pl_id, register_date) VALUES (%s, %s, %s)"
            cursor.execute(sql, (mus_id, play_list_id, datetime.datetime.now().strftime("%Y-%m-%d")))
            cursor.connection.commit()

            print()
            print("음악 추가 성공 !")

    else:
        sql = "SELECT * FROM play_list_share WHERE usr_id = %s and pl_id = %s"
        cursor.execute(sql, (id, play_list_id))
        result = cursor.fetchall()

        if (len(result) == 0):
            print()
            print("내가 생성한 플레이리스트가 아닙니다. 다시 입력하세요.")
        else:
            print()
            print("공유된 플레이리스트에는 음악을 추가할 수 없습니다.")

    my_playlist(id)


def delete_music_from_playlist(id):
    print()
    print("=============================================")
    print("|          플레이리스트에서 음악 삭제하기         |")
    print("=============================================")
    print()

    while (1):
        play_list_id = input("음악을 삭제할 플레이리스트의 id를 입력하세요 : ")
        if (play_list_id == ''):
            print("id를 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM play_list WHERE id = %s and create_usr_id = %s"
    cursor.execute(sql, (play_list_id, id))
    result = cursor.fetchall()

    if (len(result) != 0):
        print()
        print(f"플레이리스트 이름 : {result[0][2]}")
        print(f"생성 날짜 : {result[0][3]}")
        print()

        while (1):
            title = input("삭제할 음악의 제목을 입력하세요 : ")
            if (title == ''):
                print("제목을 다시 입력하세요.")
                print()
            else:
                break

        sql = "SELECT * FROM music WHERE name = %s"
        cursor.execute(sql, (title))
        result = cursor.fetchall()

        if (len(result) == 0):
            print(f"\"{title}\" 제목의 음악이 존재하지 않습니다. 다시 입력하세요.")
            my_playlist(id)
        else:
            mus_id = result[0][0]

            sql = "SELECT * FROM play_list_music WHERE mus_id = %s and pl_id = %s"
            cursor.execute(sql, (mus_id, play_list_id))
            result = cursor.fetchall()

            if (len(result) == 0):
                print()
                print("플레이리스트에 존재하지 않는 음악입니다.")
            else:
                sql = "DELETE FROM play_list_music WHERE mus_id = %s and pl_id = %s"
                cursor.execute(sql, (mus_id, play_list_id))
                cursor.connection.commit()

                print()
                print("음악 삭제 성공 !")

    else:
        sql = "SELECT * FROM play_list_share WHERE usr_id = %s and pl_id = %s"
        cursor.execute(sql, (id, play_list_id))
        result = cursor.fetchall()

        if (len(result) != 0):
            print()
            print("공유된 플레이리스트에는 음악을 삭제할 수 없습니다.")
        else:
            print()
            print("내가 생성한 플레이리스트가 아닙니다.")

    my_playlist(id)


is_playing = False
playing_time = 0
playing_timedelta = datetime.timedelta(seconds=0)
input_queue = queue.Queue()
is_like = False
is_Dislike = False
is_end = False


def display_playing_time(title, duration):
    global is_playing, playing_time, playing_timedelta, is_like, is_Dislike, is_end
    is_playing = True
    is_end = False

    while (playing_timedelta < duration):
        if not input_queue.empty():
            choice = input_queue.get()
            if (choice == 'P'):
                is_playing = False
                print()
                print("<일시정지> 'R'을 입력하면 다시 재생되고, 'E'를 입력하면 종료됩니다.")
            elif (is_playing == False and choice == 'R'):
                is_playing = True
                print("<다시 재생> 'P'를 입력하면 일시정지되고, 'E'를 입력하면 종료됩니다")
                print()
            elif (choice == 'E'):
                is_playing = False
                is_end = True
                print(f"\"{title}\" 재생이 종료되었습니다.")
                break
            elif (choice == 'L'):
                is_like = True
                is_Dislike = False
                print(f"\"{title}\"에 좋아요를 눌렀습니다.")
                print()
            elif (choice == 'D'):
                is_Dislike = True
                is_like = False
                print(f"\"{title}\"에 싫어요를 눌렀습니다.")
                print()

        if (is_playing):
            print(f"\r<{title} 재생중... {playing_timedelta} / {duration}>", end='')
            time.sleep(1)
            playing_time += 1
            hours = playing_time // 3600
            minutes = playing_time // 60
            seconds = playing_time % 60
            playing_timedelta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)

    if (playing_timedelta >= duration):
        is_playing = False
        print()
        print()
        print(f"\"{title}\" 재생이 종료되었습니다.")
        is_end = True
        print("아무 키나 입력하면 메뉴로 돌아갑니다.")


def play_music_input():
    global is_playing

    while (not input_queue.empty()):
        input_queue.get()

    while (1):
        choice = input().upper()
        if (is_end):
            break
        else:
            if (choice in ['P', 'R', 'E', 'L', 'D']):
                input_queue.put(choice)
            if (choice == 'E'):
                break


def play_music(id):
    global playing_time, playing_timedelta, is_like, is_Dislike
    print()
    print("=============================================")
    print("|                 음악 재생 메뉴             |")
    print("=============================================")
    print()

    while (1):
        title = input("재생할 음악의 제목을 입력하세요 : ")
        print()
        if (title == ''):
            print("제목을 다시 입력하세요.")
            print()
        else:
            break
    sql = "SELECT * FROM music WHERE name = %s"
    cursor.execute(sql, (title))
    result = cursor.fetchall()

    if (len(result) == 0):
        print(f"\"{title}\" 제목의 음악이 존재하지 않습니다. 메뉴로 돌아갑니다.")
        user_menu(id)
    else:
        mus_id = result[0][0]
        play_count = result[0][10] + 1
        sql = "UPDATE music SET play_count = %s WHERE id = %s"
        cursor.execute(sql, (play_count, mus_id))
        cursor.connection.commit()
        print("입력 - 'P' : 일시정지, 'R' : 다시 재생, 'E' : 종료")
        print("입력 - 'L' : 좋아요, 'D' : 싫어요")
        print()

        while (not input_queue.empty()):  # input_queue 비우기
            input_queue.get()

        threading.Thread(target=display_playing_time, args=(title, result[0][6]), daemon=True).start()

        play_music_input()

        time.sleep(1)  # Music ended message 출력을 위해 1초 대기

        sql = "INSERT INTO user_music_log (mus_id, usr_id, play_duration, play_date_time) VALUES (%s, %s, %s, %s)"
        cursor.execute(sql, (mus_id, id, playing_timedelta, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        cursor.connection.commit()
        playing_time = 0
        playing_timedelta = datetime.timedelta(seconds=0)

        if (is_like):
            sql = "select * from like_music where usr_id = %s and mus_id = %s"
            cursor.execute(sql, (id, mus_id))
            result = cursor.fetchall()

            if (len(result) == 0):
                sql = "INSERT INTO like_music (usr_id, mus_id, like_date) VALUES (%s, %s, %s)"
                cursor.execute(sql, (id, mus_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                cursor.connection.commit()

                sql = "UPDATE music SET like_count = like_count + 1 WHERE id = %s"
                cursor.execute(sql, (mus_id))
                cursor.connection.commit()

                sql = "SELECT * FROM dislike_music WHERE usr_id = %s and mus_id = %s"
                cursor.execute(sql, (id, mus_id))
                result = cursor.fetchall()
                if (len(result) != 0):
                    sql = "DELETE FROM dislike_music WHERE usr_id = %s and mus_id = %s"
                    cursor.execute(sql, (id, mus_id))
                    cursor.connection.commit()

        elif (is_Dislike):
            sql = "SELECT * FROM dislike_music WHERE usr_id = %s and mus_id = %s"
            cursor.execute(sql, (id, mus_id))
            result = cursor.fetchall()

            if (len(result) == 0):
                sql = "INSERT INTO dislike_music (usr_id, mus_id, dislike_date) VALUES (%s, %s, %s)"
                cursor.execute(sql, (id, mus_id, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                cursor.connection.commit()
                sql = "SELECT * FROM like_music WHERE usr_id = %s and mus_id = %s"
                cursor.execute(sql, (id, mus_id))
                result = cursor.fetchall()

                if (len(result) != 0):
                    sql = "DELETE FROM like_music WHERE usr_id = %s and mus_id = %s"
                    cursor.execute(sql, (id, mus_id))
                    cursor.connection.commit()
                    sql = "UPDATE music SET like_count = like_count - 1 WHERE id = %s"
                    cursor.execute(sql, (mus_id))
                    cursor.connection.commit()

        user_menu(id)


def search_music(id):
    print()
    print("=============================================")
    print("|                음악 검색 메뉴              |")
    print("=============================================")
    print()

    while (1):
        title = input("검색할 음악의 제목을 입력하세요 : ")
        print()
        if (title == ''):
            print("제목을 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM music WHERE name LIKE %s"
    cursor.execute(sql, ('%' + title + '%'))
    result = cursor.fetchall()

    if (len(result) == 0):
        print(f"\"{title}\" 제목의 음악이 존재하지 않습니다. 다시 입력하세요.")
        user_menu(id)
    else:
        for music in result:
            sql = "SELECT * FROM music_artist WHERE mus_id = %s"
            cursor.execute(sql, (music[0]))
            artist = cursor.fetchall()
            print(f"음악 id : {music[0]}")
            print(f"제목 : {music[2]}")
            for artist_ in artist:
                print(f"아티스트 : {artist_[1]}")
            print(f"앨범 : {music[3]}")
            print(f"장르 : {music[4]}")
            print(f"발매일 : {music[9]}")
            print()
        user_menu(id)


def search_artist(id):
    print()
    print("=============================================")
    print("|              아티스트 검색 메뉴             |")
    print("=============================================")
    print()

    while (1):
        artist = input("검색할 아티스트의 이름을 입력하세요 : ")
        print()
        if (artist == ''):
            print("아티스트 이름을 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM music_artist WHERE mus_artist LIKE %s"
    cursor.execute(sql, ('%' + artist + '%'))
    result = cursor.fetchall()

    if (len(result) == 0):
        print(f"{artist} 이름의 아티스트가 존재하지 않습니다. 다시 입력하세요.")
        user_menu(id)
    else:
        for artist in result:
            print(f"아티스트 이름 : {artist[1]}")
            sql = "SELECT * FROM music WHERE id = %s"
            cursor.execute(sql, (artist[0]))
            music = cursor.fetchall()
            for m in music:
                print(f"음악 제목 : {m[2]}")
                print()
        user_menu(id)


def show_top_10_music(id, table):
    print()
    print("=============================================")
    print("|           Top 10 Music 목록 보기         |")
    print("=============================================")
    print()

    sql = f"SELECT * FROM music ORDER BY {table} DESC LIMIT 10"
    cursor.execute(sql)
    result = cursor.fetchall()

    if (len(result) == 0):
        print("음악이 존재하지 않습니다.")
        user_menu(id)
    else:
        print()
        for i, music in enumerate(result):
            print(f"<Top {i + 1} Music>")
            print(f"음악 id : {music[0]}")
            print(f"제목 : {music[2]}")
            if (table == 'play_count'):
                print(f"재생 횟수 : {music[10]}")
            elif (table == 'like_count'):
                print(f"좋아요 수 : {music[12]}")
            print()
        user_menu(id)


def admin_menu(id):

    print()
    print("=============================================")
    print("|                 관리자 메뉴               |")
    print("=============================================")
    print()
    sql = 'SELECT * FROM admin WHERE id = %s'
    cursor.execute(sql, (id))
    result = cursor.fetchall()
    print(f"안녕하세요, {result[0][3]}님 !")
    sql = 'SELECT * FROM admin_role WHERE adm_id = %s'
    cursor.execute(sql, (id))
    result = cursor.fetchall()
    for (i, role) in enumerate(result):
        if (role[1] == 'music_manager'):
            print(f"역할{i+1} : 음악 관리자")
        elif (role[1] == 'user_manager'):
            print(f"역할{i+1} : 사용자 관리자")
        elif (role[1] == 'system_manager'):
            print(f"역할{i+1} : 시스템 관리자")
    print()
    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()

    print("1. 음악 관리")
    print("2. 사용자 관리")
    print("3. 시스템 관리")
    print("4. 로그아웃")
    print("5. 계정 삭제")
    print("6. 종료")
    print()
    choice = input("선택(1~6) : ")

    if (choice == '1'):
        sql = 'SELECT adm_role FROM admin_role WHERE adm_id = %s'
        cursor.execute(sql, (id))
        result = cursor.fetchall()

        for role in result:
            if (role[0] == admin_roles_list[0]):
                manage_music(id)
                return

        print("당신은 음악 관리자가 아닙니다. 다른 메뉴를 선택하세요.")
        admin_menu(id)

    elif (choice == '2'):
        sql = 'SELECT adm_role FROM admin_role WHERE adm_id = %s'
        cursor.execute(sql, (id))
        result = cursor.fetchall()

        for role in result:
            if (role[0] == admin_roles_list[1]):
                manage_user(id)
                return

        print("당신은 사용자 관리자가 아닙니다. 다른 메뉴를 선택하세요.")
        admin_menu(id)

    elif (choice == '3'):
        sql = 'SELECT adm_role FROM admin_role WHERE adm_id = %s'
        cursor.execute(sql, (id))
        result = cursor.fetchall()

        for role in result:
            if (role[0] == admin_roles_list[2]):
                manage_system(id)
                return

        print("당신은 시스템 관리자가 아닙니다. 다른 메뉴를 선택하세요.")
        admin_menu(id)

    elif (choice == '4'):
        print()
        print("로그아웃 되었습니다.")
        login_menu()

    elif (choice == '5'):
        print()
        check = input("정말로 계정을 삭제하시겠습니까? (Y/N) : ")
        check = check.upper()
        if (check == 'Y'):
            sql = "DELETE FROM admin WHERE id = %s"
            cursor.execute(sql, (id))
            cursor.connection.commit()
            print("계정이 삭제되었습니다.")
            login_menu()
        elif (check == 'N'):
            print()
            print("계정 삭제가 취소되었습니다.")
            admin_menu(id)
        else:
            print("잘못된 입력입니다. 다시 시도해주세요")
            admin_menu(id)

    elif (choice == '6'):
        print("안녕히 가세요 !")
        exit()
    else:
        print("잘못된 선택입니다. 다시 시도해주세요.")
        print()
        admin_menu(id)


def manage_music(id):
    print()
    print("=============================================")
    print("|               음악 관리 메뉴               |")
    print("=============================================")
    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()

    print("1. 음악 등록")
    print("2. 음악 삭제")
    print("3. 내가 등록한 음악 목록 보기")
    print("4. 관리자 메뉴로 돌아가기")
    print("5. 종료")
    print()

    choice = input("선택(1~5) : ")

    if (choice == '1'):
        register_music(id)
    elif (choice == '2'):
        delete_music(id)
    elif (choice == '3'):
        list_music(id)
    elif (choice == '4'):
        admin_menu(id)
    elif (choice == '5'):
        print("안녕히 가세요 !")
        exit()
    else:
        print("잘못된 선택입니다. 다시 시도해주세요.")
        manage_music(id)


def register_music(id):
    print()
    print("=============================================")
    print("|               음악 등록 메뉴               |")
    print("=============================================")
    print()

    adm_id = id

    while (1):
        title = input("추가할 음악의 제목을 입력하세요(Max 50 characters) : ")
        if (title == '' or len(title) > 50):
            print("Please enter the title again.")
            print()
        else:
            sql = "SELECT * FROM music WHERE name = %s"
            cursor.execute(sql, (title))
            result = cursor.fetchall()
            if (len(result) != 0):
                print("이미 존재하는 음악입니다. 다른 음악을 입력하세요.")
                print()
            else:
                break

    artist_list = []
    while (1):
        print()
        print("아티스트 이름을 입력하세요.(최대 30자)")
        print("여러 명의 아티스트가 있을 경우 하나씩 입력 후, 'done'을 입력하세요.")
        artist = input(": ")
        if (artist == '' or len(artist) > 30):
            print("다시 입력하세요.")
            print()
        elif (artist in artist_list):
            print("이미 입력한 아티스트입니다. 다시 입력하세요.")
            print()
        elif (artist == 'done'):
            break
        else:
            artist_list.append(artist)

    while (1):
        print()
        album = input("앨범 제목을 입력하세요(Max 50 characters) : ")
        if (album == '' or len(album) > 50):
            print("다시 입력하세요.")
            print()
        else:
            break

    while (1):
        print()
        print("장르를 선택하세요.")
        print("B(ballad), K(kpop), P(pop), R(rnb), D(dance), H(hiphop), Rc(rock), J(jazz), C(classic), E(etc)")
        genre = input(": ")
        genre = genre.upper()

        if genre == 'B':
            genre = genre_list[0]
            break
        elif genre == 'K':
            genre = genre_list[1]
            break
        elif genre == 'P':
            genre = genre_list[2]
            break
        elif genre == 'R':
            genre = genre_list[3]
            break
        elif genre == 'D':
            genre = genre_list[4]
            break
        elif genre == 'H':
            genre = genre_list[5]
            break
        elif genre == 'Rc':
            genre = genre_list[6]
            break
        elif genre == 'J':
            genre = genre_list[7]
            break
        elif genre == 'C':
            genre = genre_list[8]
            break
        elif genre == 'E':
            genre = genre_list[9]
            break
        else:
            print("잘못된 입력입니다. 다시 시도해주세요.")
            print()

    while (1):
        print()
        lyrics_file_path = input("가사 파일의 경로를 입력하세요 : ")
        if (lyrics_file_path == ''):
            print("다시 입력하세요.")
            print()
        else:
            break

    while (1):
        print()
        duration = input("음악의 재생 시간을 입력하세요(HH:MM:SS) : ")
        try:
            datetime.datetime.strptime(duration, "%H:%M:%S")
            break
        except ValueError:
            print("잘못된 형식의 재생 시간입니다. 다시 입력하세요.")
            print()

    while (1):
        print()
        cover_img_path = input("커버 이미지 파일의 경로를 입력하세요 : ")
        if (cover_img_path == ''):
            print("다시 입력하세요.")
            print()
        else:
            break

    while (1):
        print()
        file_path = input("음악 파일의 경로를 입력하세요 : ")
        if (file_path == ''):
            print("다시 입력하세요.")
            print()
        else:
            break

    while (1):
        print()
        release_date = input("음악의 발매일을 입력하세요(YYYY-MM-DD) : ")
        try:
            datetime.datetime.strptime(release_date, "%Y-%m-%d")
            break
        except ValueError:
            print("잘못된 형식의 발매일입니다. 다시 입력하세요.")
            print()

    register_date = datetime.datetime.now().strftime("%Y-%m-%d")

    sql = "INSERT INTO music (adm_id, name, album, genre, lyrics_file_path, duration, cover_img_path, file_path, release_date, register_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(sql, (adm_id, title, album, genre, lyrics_file_path, duration,
                   cover_img_path, file_path, release_date, register_date))
    cursor.connection.commit()

    mus_id = cursor.lastrowid

    sql = "INSERT INTO music_artist (mus_id, mus_artist) VALUES (%s, %s)"
    for artist_ in artist_list:
        cursor.execute(sql, (mus_id, artist_))

    cursor.connection.commit()

    print()
    print("음악 등록 성공 !")
    manage_music(id)


def delete_music(id):
    print()
    print("=============================================")
    print("|               음악 삭제 메뉴               |")
    print("=============================================")
    print()

    while (1):
        title = input("삭제할 음악의 제목을 입력하세요 : ")
        if (title == ''):
            print("다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM music WHERE name = %s"
    cursor.execute(sql, (title))
    result = cursor.fetchall()

    if (len(result) == 0):
        print(f"\"{title}\" 제목의 음악이 존재하지 않습니다. 다시 입력하세요.")
        delete_music(id)
    else:
        mus_id = result[0][0]
        sql = "DELETE FROM music WHERE id = %s"
        cursor.execute(sql, (mus_id))
        cursor.connection.commit()

        print()
        print("음악 삭제 성공 !")
        manage_music(id)


def list_music(id):
    print()
    print("=============================================")
    print("|           내가 등록한 음악 목록 보기          |")
    print("=============================================")
    print()

    sql = "SELECT * FROM music WHERE adm_id = %s"
    cursor.execute(sql, (id))
    result = cursor.fetchall()

    if (len(result) == 0):
        print("아직 당신이 등록한 음악이 없습니다.")
        manage_music(id)
    else:
        for music in result:
            print(f"음악 id : {music[0]}")
            print(f"제목 : {music[2]}")
            sql = "SELECT * FROM music_artist WHERE mus_id = %s"
            cursor.execute(sql, (music[0]))
            artist = cursor.fetchall()
            for artist_ in artist:
                print(f"아티스트 : {artist_[1]}")
            print(f"앨범 : {music[3]}")
            print(f"장르 : {music[4]}")
            print(f"재생 시간 : {music[6]}")
            print()
        manage_music(id)


def manage_user(id):
    print()
    print("=============================================")
    print("|              사용자 관리 메뉴              |")
    print("=============================================")
    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()

    print("1. 사용자 검색")
    print("2. 사용자 삭제")
    print("3. 관리자 메뉴로 돌아가기")
    print("4. 종료")
    print()
    choice = input("선택(1~4) : ")

    if (choice == '1'):
        search_user(id, from_admin=True)
    elif (choice == '2'):
        delete_user(id)
    elif (choice == '3'):
        admin_menu(id)
    elif (choice == '4'):
        print("안녕히 가세요 !")
        exit()
    else:
        print("잘못된 선택입니다. 다시 시도해주세요.")
        manage_user(id)


def search_user(id, from_admin=False):
    print()
    print("=============================================")
    print("|              사용자 검색 메뉴              |")
    print("=============================================")
    print()

    while (1):
        name = input("검색할 사용자의 이름을 입력하세요 : ")
        if (name == ''):
            print("이름을 다시 입력하세요.")
            print()
        else:
            break

    sql = "SELECT * FROM user WHERE name LIKE %s"
    cursor.execute(sql, ('%' + name + '%'))
    result = cursor.fetchall()

    if (len(result) == 0):
        print(f"{name} 이름의 사용자가 존재하지 않습니다. 다시 입력하세요.")
        if (from_admin):
            manage_user(id)
        else:
            user_menu(id)
    else:
        print()
        for user in result:
            print(f"사용자 id : {user[0]}")
            print(f"이름 : {user[1]}")
            print(f"이메일 : {user[2]}")
            print(f'생년월일 : {user[6]}')
            print()
        if (from_admin):
            manage_user(id)
        else:
            user_menu(id)


def delete_user(id):
    print()
    print("=============================================")
    print("|             사용자 계정 삭제 메뉴           |")
    print("=============================================")
    print()

    while (1):
        usr_id = input("삭제할 사용자의 usr_id를 입력하세요 : ")
        if (usr_id == ''):
            print("id를 다시 입력하세요.")
            print()
        else:
            check = input("정말로 삭제하시겠습니까? (Y/N) : ")
            check = check.upper()
            if (check == 'Y'):
                sql = "SELECT * FROM user WHERE id = %s"
                cursor.execute(sql, (usr_id))
                result = cursor.fetchall()
                if (len(result) == 0):
                    print(f"{usr_id} id의 사용자가 존재하지 않습니다. 다시 입력하세요.")
                    manage_user(id)
                else:
                    sql = "DELETE FROM user WHERE id = %s"
                    cursor.execute(sql, (usr_id))
                    cursor.connection.commit()

                    print()
                    print("사용자 삭제 성공 !")
                    manage_user(id)
            elif (check == 'N'):
                print()
                print("사용자 삭제가 취소되었습니다.")
                manage_user(id)
            else:
                print("잘못된 입력입니다. 다시 시도해주세요.")
                print()
            break


def manage_system(id):
    print()
    print("=============================================")
    print("|              시스템 관리 메뉴              |")
    print("=============================================")
    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()

    print("1. 모든 관리자 보기")
    print("2. 관리자의 역할 변경")
    print("3. 관리자 메뉴로 돌아가기")
    print("4. 종료")
    print()
    choice = input("선택(1~4) : ")

    if (choice == '1'):
        list_all_admins(id)
    elif (choice == '2'):
        change_role_of_admin(id)
    elif (choice == '3'):
        admin_menu(id)
    elif (choice == '4'):
        print("안녕히 가세요 ! ")
        exit()
    else:
        print("잘못된 선택입니다. 다시 시도해주세요.")
        manage_system(id)


def list_all_admins(id):
    print()
    print("=============================================")
    print("|             모든 관리자 목록 보기           |")
    print("=============================================")
    print()

    sql = "SELECT * FROM admin"
    cursor.execute(sql)
    result = cursor.fetchall()

    if (len(result) == 0):
        print("아직 관리자가 존재하지 않습니다.")
        manage_system(id)
    else:
        for admin in result:
            print(f"관리자 id : {admin[0]}")
            print(f"이름 : {admin[3]}")
            print(f"이메일 : {admin[4]}")
            sql = "SELECT adm_role FROM admin_role WHERE adm_id = %s"
            cursor.execute(sql, (admin[0]))
            role = cursor.fetchall()
            for r in role:
                if (r[0] == admin_roles_list[0]):
                    print("역할 : 음악 관리자")
                elif (r[0] == admin_roles_list[1]):
                    print("역할 : 사용자 관리자")
                elif (r[0] == admin_roles_list[2]):
                    print("역할 : 시스템 관리자")
            print()
        manage_system(id)


def change_role_of_admin(id):
    print()
    print("=============================================")
    print("|            관리자의 역할 변경 메뉴           |")
    print("=============================================")
    print("아래의 메뉴 중 하나를 선택하세요 :")
    print()
    print("1. 역할 추가")
    print("2. 역할 삭제")
    print("3. 시스템 관리자 메뉴로 돌아가기")
    print()
    choice = input("선택(1~3) : ")

    if (choice == '1'):
        while (1):
            adm_id = input("역할을 추가할 관리자의 id를 입력하세요 : ")
            if (adm_id == ''):
                print("id를 다시 입력하세요.")
                print()
            else:
                sql = "SELECT * FROM admin WHERE id = %s"
                cursor.execute(sql, (adm_id))
                result = cursor.fetchall()
                if (len(result) == 0):
                    print(f"{adm_id} id의 관리자가 존재하지 않습니다. 다시 입력하세요.")
                    manage_system(id)
                else:
                    add_role(id, adm_id)

    elif (choice == '2'):
        while (1):
            adm_id = input("역할을 삭제할 관리자의 id를 입력하세요 : ")
            if (adm_id == ''):
                print("id를 다시 입력하세요.")
                print()
            else:
                sql = "SELECT * FROM admin WHERE id = %s"
                cursor.execute(sql, (adm_id))
                result = cursor.fetchall()
                if (len(result) == 0):
                    print(f"{adm_id} id의 관리자가 존재하지 않습니다. 다시 입력하세요.")
                    manage_system(id)
                else:
                    delete_role(id, adm_id)

    elif (choice == '3'):
        manage_system(id)
    else:
        print("잘못된 선택입니다. 다시 시도해주세요.")
        change_role_of_admin(id)


def add_role(id, adm_id):
    print()
    print("=============================================")
    print("|             관리자 역할 추가 메뉴           |")
    print("=============================================")
    print()

    role_list = []
    sql = "SELECT adm_role FROM admin_role WHERE adm_id = %s"
    cursor.execute(sql, (adm_id))
    result = cursor.fetchall()
    print("<관리자의 현재 역할>")
    for role in result:
        if (role[0] == admin_roles_list[0]):
            print("음악 관리자")
        elif (role[0] == admin_roles_list[1]):
            print("사용자 관리자")
        elif (role[0] == admin_roles_list[2]):
            print("시스템 관리자")
        role_list.append(role[0])
    print()

    print("추가할 역할을 입력하세요. ('M' : 음악 관리자, 'U' : 사용자 관리자, 'S' : 시스템 관리자)")
    role = input(": ")
    role = role.upper()

    if (role == 'M'):
        role = admin_roles_list[0]
    elif (role == 'U'):
        role = admin_roles_list[1]
    elif (role == 'S'):
        role = admin_roles_list[2]
    else:
        print("잘못된 역할입니다. 다시 입력하세요.")
        add_role(id, adm_id)

    if (role in role_list):
        print("이미 존재하는 역할입니다. 다른 역할을 입력하세요.")
        change_role_of_admin(id)
    else:
        sql = "INSERT INTO admin_role (adm_id, adm_role) VALUES (%s, %s)"
        cursor.execute(sql, (adm_id, role))
        cursor.connection.commit()

        print()
        print("역할 추가 성공 !")
        change_role_of_admin(id)


def delete_role(id, adm_id):
    print()
    print("=============================================")
    print("|             관리자 역할 삭제 메뉴           |")
    print("=============================================")
    print()

    role_list = []
    sql = "SELECT adm_role FROM admin_role WHERE adm_id = %s"
    cursor.execute(sql, (adm_id))
    result = cursor.fetchall()
    print("<관리자의 현재 역할>")
    for role in result:
        if (role[0] == admin_roles_list[0]):
            print("음악 관리자")
        elif (role[0] == admin_roles_list[1]):
            print("사용자 관리자")
        elif (role[0] == admin_roles_list[2]):
            print("시스템 관리자")
        role_list.append(role[0])
    print()

    print("삭제할 역할을 입력하세요. ('M' : 음악 관리자, 'U' : 사용자 관리자, 'S' : 시스템 관리자)")
    role = input(": ")
    role = role.upper()

    if (role == 'M'):
        role = admin_roles_list[0]
    elif (role == 'U'):
        role = admin_roles_list[1]
    elif (role == 'S'):
        role = admin_roles_list[2]
    else:
        print("잘못된 역할입니다. 다시 입력하세요.")
        delete_role(id, adm_id)

    if (role not in role_list):
        print("존재하지 않는 역할입니다. 다시 입력하세요.")
        change_role_of_admin(id)
    else:
        sql = "DELETE FROM admin_role WHERE adm_id = %s AND adm_role = %s"
        cursor.execute(sql, (adm_id, role))
        cursor.connection.commit()

        print()
        print("역할 삭제 성공 !")
        change_role_of_admin(id)


if __name__ == '__main__':
    print()
    print("음악 스트리밍 서비스에 오신 것을 환영합니다 !")
    login_menu()
