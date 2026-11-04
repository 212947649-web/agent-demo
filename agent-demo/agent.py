import json, os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com",
)

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path: str, content: str) -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"ok: wrote {path}"

def calc(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}, {}))

TOOLS = [
    {"type": "function", "function": {"name": "read_file", "description": "读文件", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}},
    {"type": "function", "function": {"name": "calc", "description": "计算", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "写文件", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
]
DISPATCH = {"read_file": read_file, "calc": calc, "write_file": write_file}

def run_agent(goal: str, max_steps: int = 8):
    messages = [
        {"role": "system", "content": "你会用工具。先读 shop.txt，把价格加总，把总数写入 bill.txt。"},
        {"role": "user", "content": goal},
    ]
    for step in range(1, max_steps + 1):
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, tools=TOOLS)
        msg = resp.choices[0].message
        messages.append(msg)
        if not msg.tool_calls:
            print("最终回答:", msg.content)
            return
        for call in msg.tool_calls:
            name, args = call.function.name, json.loads(call.function.arguments or "{}")
            print(f"[step {step}] {name}({args})")
            result = DISPATCH[name](**args)
            print("观察:", result[:200])
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})

if __name__ == "__main__":
    run_agent("统计 shop.txt 总价，写入 bill.txt")