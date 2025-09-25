from app import create_app  # 从 app 包中导入 create_app 函数

app = create_app()  # 创建 Flask 应用实例

if __name__ == '__main__':
    app.run(debug=True)  # 运行 Flask 应用
