import requests
import json
import traceback

def test_api():
    base_url = "http://127.0.0.1:5000"
    
    # 1. 测试今日统计
    print("-" * 30)
    print("测试今日统计 API...")
    try:
        resp = requests.get(f"{base_url}/api/stats/today", timeout=10)
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            print("响应数据:", json.dumps(resp.json(), indent=2, ensure_ascii=False))
        else:
            print("错误信息:")
            print(resp.text[:2000])
    except Exception as e:
        print(f"请求失败: {e}")
        traceback.print_exc()

    # 2. 测试刷新数据
    print("\n" + "-" * 30)
    print("测试刷新数据 API...")
    try:
        resp = requests.post(
            f"{base_url}/api/spider/refresh", 
            json={"page_num": 1},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            print("响应数据:", json.dumps(resp.json(), indent=2, ensure_ascii=False))
        else:
            print("错误信息:")
            print(resp.text[:2000])
    except Exception as e:
        print(f"请求失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
