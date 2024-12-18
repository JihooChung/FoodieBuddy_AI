import paramiko
from sshtunnel import SSHTunnelForwarder
import pymysql

# EC2 연결 설정
ssh_host = '54.180.105.172'
ssh_user = 'ubuntu'
ssh_key_file = 'foodiebuddy-ec2-key.pem'  # 구글 코랩에 PEM 키 파일을 업로드한 후 경로를 입력

# RDS 데이터베이스 설정
rds_host = 'foodiebuddy-rds.clo8m062s7ci.ap-northeast-2.rds.amazonaws.com'
rds_port = 3306  # MySQL 예시, 사용하는 데이터베이스에 맞춰 설정

# SSH 터널 설정
# 1. Try using a different local bind port to avoid conflicts.
#    For example, change 3306 to 3307:
# local_bind_address=('127.0.0.1', 3307)
server = SSHTunnelForwarder(
    (ssh_host, 22),
    ssh_username=ssh_user,
    ssh_pkey=ssh_key_file,
    remote_bind_address=(rds_host, rds_port),
    local_bind_address=('127.0.0.1', 3307)  # 로컬 머신에서 3307 포트를 통해 연결
)

# 2. Add exception handling and logging for better debugging:
try:
    server.start()
    print(f"SSH 터널이 열렸습니다. 로컬 포트 {server.local_bind_port}을 통해 RDS에 연결할 수 있습니다.")
except Exception as e:
    print(f"SSH 터널을 여는 동안 오류가 발생했습니다: {e}")
    # Consider adding more detailed logging here to troubleshoot the error.
    import traceback
    traceback.print_exc()
    # You can also check the server logs for more information about the error.



# ... (rest of your code remains the same, but update the port)

connection = pymysql.connect(
    host='127.0.0.1',  # 로컬 호스트에서 접근
    user='admin',
    password='',
    db='foodiebuddy', # foodiebuddy: 스키마 이름
    port=server.local_bind_port  # SSH 터널의 포트 (server.local_bind_port 사용)
)

#유저 한명 식이제한 불러오기
cursor = connection.cursor()
cursor.execute("SHOW COLUMNS FROM user")
diets_list = cursor.fetchall()

cursor.execute("SELECT * FROM user Where email='email1@gmail.com'") # user: 테이블 이름
user_diets = list(cursor.fetchall()[0])
user_info = {}

for i in range(len(diets_list)):
    if diets_list[i][0] not in ('user_id', 'email', 'password', 'username'):
        user_info[diets_list[i][0]] = user_diets[i]

print(user_info)

str_user_diet = f"Religion: {user_info['religion']}, Vegetarian: {user_info['vegetarian']}. Details: "
for k, v in user_info.items():
    if k == 'vegetarian' or k == 'religion':
        continue
    if v is None or v == b'\x00':
        continue

    if v == b'\x01':
        str_user_diet += k + ', '
    else:
        str_user_diet += k + ':' + v + ', '

str_user_diet = str_user_diet[:-2]+'.'
print(str_user_diet) #str_user_diet만 이걸로 대체하면 됨
