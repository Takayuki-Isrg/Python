#上のよりもっと速い方法
# 2に対して2より大きい偶数を削除し、3に対して3より大きく3で割れる数を排除し・・・
# としていくので無駄なチェックが減っている
MAX = 100
LIST = range(2, MAX + 1)
for i in range(2, int(MAX ** 0.5)):
    LIST = [x for x in LIST if (x == i or x % i != 0)]

# for j in LIST:
    # print (j)

for j in LIST:
    if i == j:
        print('素数を数えて落ち着くんだ・・・', end='\n')

# for i in range(1, MAX + 1):
    