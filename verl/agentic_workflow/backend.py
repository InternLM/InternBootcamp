def query(prompt: str) -> str:
    from openai import OpenAI
    model_name = 'deepseekv3-1-terminus'
    # 创建 OpenAI 客户端
    client = OpenAI(
        api_key= model_name,
        base_url='http://100.96.35.28:18889/v1/'  # 自定义部署或代理地址
    )
    # 构造对话请求
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.001,
        max_tokens=16384,
        timeout=100
    )

    # 输出结果
    return response.choices[0].message.content


if __name__ == "__main__":
    prompt = "hello, how are you?"
    print(query(prompt))