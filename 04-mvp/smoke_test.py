import requests
import sys
from time import sleep

BASE = "http://localhost:8000"
headers = {"X-User-Id": "user-admin-001"}

def check(method, url, expected=200, **kwargs):
    r = requests.request(method, url, **kwargs)
    status = "OK" if r.status_code == expected else "FAIL"
    print(f"  [{status}] {method} {url} -> {r.status_code} (expected {expected})")
    return r.status_code == expected

def main():
    # Wait for server
    for i in range(5):
        try:
            r = requests.get(f"{BASE}/api/biz")
            if r.status_code == 200:
                break
        except:
            pass
        sleep(1)

    print("Running smoke tests...")
    all_ok = True

    # biz_kl
    all_ok &= check("GET", f"{BASE}/api/biz")
    all_ok &= check("GET", f"{BASE}/api/biz?status=published")

    r = check("GET", f"{BASE}/api/biz")
    if r:
        items = requests.get(f"{BASE}/api/biz").json()
        if items:
            bid = items[0]["id"]
            all_ok &= check("GET", f"{BASE}/api/biz/{bid}")
            all_ok &= check("PUT", f"{BASE}/api/biz/{bid}", json={"name": "Updated Name"}, headers={**headers, "Content-Type": "application/json"})

    # sys_kl
    all_ok &= check("GET", f"{BASE}/api/sys")
    all_ok &= check("GET", f"{BASE}/api/sys?layer=domain")

    r2 = check("GET", f"{BASE}/api/sys")
    if r2:
        items = requests.get(f"{BASE}/api/sys").json()
        if items:
            sid = items[0]["id"]
            all_ok &= check("GET", f"{BASE}/api/sys/{sid}")

    # audit
    all_ok &= check("GET", f"{BASE}/api/audit")

    # package
    r3 = requests.get(f"{BASE}/api/biz?status=published")
    if r3.status_code == 200 and r3.json():
        biz_ids = ",".join([i["id"] for i in r3.json()[:2]])
        all_ok &= check("GET", f"{BASE}/api/packages?biz_ids={biz_ids}")
        all_ok &= check("GET", f"{BASE}/api/packages/{biz_ids}.md")

    # html pages
    all_ok &= check("GET", f"{BASE}/")
    all_ok &= check("GET", f"{BASE}/biz")
    all_ok &= check("GET", f"{BASE}/sys")
    all_ok &= check("GET", f"{BASE}/export")
    all_ok &= check("GET", f"{BASE}/audit")
    all_ok &= check("GET", f"{BASE}/import")

    if all_ok:
        print("\nAll smoke tests passed!")
        sys.exit(0)
    else:
        print("\nSome smoke tests FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
