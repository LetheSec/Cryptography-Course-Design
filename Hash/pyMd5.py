
import hashlib
import time

message = "My name is YuanXiaojian, I am from CUMT." * 5000000
# MD5
digest = hashlib.md5()
digest.update(message.encode())
start = time.perf_counter()
res = digest.hexdigest()
end = time.perf_counter()
print("md5: " + res)
print("Spend time: " + str(end - start) + " seconds.\n")

# SHA1
digest = hashlib.sha1()
digest.update(message.encode())
start = time.perf_counter()
res = digest.hexdigest()
end = time.perf_counter()
print("sha1: " + res)
print("Spend time: " + str(end - start) + " seconds.\n")

# SHA256
digest = hashlib.sha256()
digest.update(message.encode())
start = time.perf_counter()
res = digest.hexdigest()
end = time.perf_counter()
print("sha256: " + res)
print("Spend time: " + str(end - start) + " seconds.\n")

# SHA512
digest = hashlib.sha512()
digest.update(message.encode())
start = time.perf_counter()
res = digest.hexdigest()
end = time.perf_counter()
print("sha512: " + res)
print("Spend time: " + str(end - start) + " seconds.")