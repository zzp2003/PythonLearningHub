def generate_pascal_triangle(n):
    # 初始化杨辉三角形
    triangle = []
    for i in range(n):
        # 每一行的第一个元素都是1
        row = [1]
        if triangle:  # 如果不是第一行
            last_row = triangle[-1]
            # 计算当前行的中间元素
            for j in range(len(last_row) - 1):
                row.append(last_row[j] + last_row[j + 1])
            # 每一行的最后一个元素都是1
            row.append(1)
        triangle.append(row)
    return triangle

def print_pascal_triangle(triangle):
    # 获取最后一行的字符串长度作为对齐参考
    max_width = len(' '.join(map(str, triangle[-1])))
    
    # 打印每一行
    for row in triangle:
        # 将数字转换为字符串并用空格连接
        row_str = ' '.join(map(str, row))
        # 居中对齐输出
        print(row_str.center(max_width))

def main():
    # 生成至少8行的杨辉三角形
    n = 9
    triangle = generate_pascal_triangle(n)
    print(f"杨辉三角形 ({n} 行):")
    print_pascal_triangle(triangle)

if __name__ == '__main__':
    main()