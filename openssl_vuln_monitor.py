import re
import json
# import smtplib
import requests
# from email.mime.text import MIMEText
from pathlib import Path
from winotify import Notification, audio
import time
from datetime import datetime

CONFIG = {
    "url": "https://openssl-library.org/news/vulnerabilities/",
    "known_file": Path(__file__).parent / "known_cves.json",
    # "smtp_server": "smtp.qq.com",
    # "smtp_port": 465,
    # "smtp_user": "xxx@qq.com",
    # "smtp_pass": "xxx",
    # "mail_to": "xxx@qq.com",
}

CVE_PATTERN = re.compile(r'CVE-\d{4}-\d{4,7}', re.IGNORECASE)
CVE_BLOCK_PATTERN = re.compile(
    r'<[^>]*>\s*CVE-(\d{4})-(\d{4,7})\s*</[^>]*>(.*?)(?=<[^>]*>\s*CVE-\d{4}-\d{4,7}\s*</[^>]*>|<h2\s|$/)',
    re.DOTALL | re.IGNORECASE,
)
AFFECTED_PATTERN = re.compile(
    r'Affected\s*</span>\s*</div>\s*<div[^>]*>\s*<ul>\s*(.*?)\s*</ul>',
    re.DOTALL,
)
AFFECTED_ITEM_PATTERN = re.compile(r'from\s+([\d.]+[a-z]*)\s+before\s+[\d.]+[a-z]*')
SEVERITY_PATTERN = re.compile(r'Severity\s*</span>\s*</div>\s*<div[^>]*>\s*(.*?)\s*</div>', re.DOTALL)
TITLE_PATTERN = re.compile(r'Title\s*</span>\s*</div>\s*<div[^>]*>\s*(.*?)\s*</div>', re.DOTALL)

HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
WHITESPACE_PATTERN = re.compile(r'\s+')


def strip_html(text):
    text = HTML_TAG_PATTERN.sub('', text)
    text = WHITESPACE_PATTERN.sub(' ', text)
    return text.strip()


def fetch_page():
    resp = requests.get(CONFIG["url"], timeout=30)
    resp.raise_for_status()
    return resp.text


def classify_branch(from_ver):
    parts = from_ver.split('.')
    try:
        major = int(parts[0])
    except (ValueError, IndexError):
        return None
    minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
    if major == 1:
        return "1.1"
    if major == 3 and minor == 0:
        return "3.0"
    if major == 3 and minor in (4, 5):
        return "3.5"
    if (major == 3 and minor >= 6) or major >= 4:
        return "3.6+"
    return None


def extract_cves(html):
    cve_ids = set(CVE_PATTERN.findall(html))
    cve_ids = {c.upper() for c in cve_ids}
    details = {}
    for m in CVE_BLOCK_PATTERN.finditer(html):
        year, num = m.group(1), m.group(2)
        cve_id = f"CVE-{year}-{num}"
        block = m.group(0)
        title_m = TITLE_PATTERN.search(block)
        severity_m = SEVERITY_PATTERN.search(block)
        title = strip_html(title_m.group(1)) if title_m else "未知"
        severity = strip_html(severity_m.group(1)) if severity_m else "未知"
        aff_match = AFFECTED_PATTERN.search(block)
        branches = set()
        if aff_match:
            for item in AFFECTED_ITEM_PATTERN.finditer(aff_match.group(1)):
                from_ver = item.group(1)
                branch = classify_branch(from_ver)
                if branch:
                    branches.add(branch)
        details[cve_id] = {"title": title, "severity": severity, "branches": branches}
    return cve_ids, details


def load_known():
    f = CONFIG["known_file"]
    if f.exists():
        with open(f, 'r', encoding='utf-8') as fh:
            return set(json.load(fh))
    return set()


def save_known(cve_set):
    with open(CONFIG["known_file"], 'w', encoding='utf-8') as fh:
        json.dump(sorted(cve_set), fh, ensure_ascii=False, indent=2)


def build_notify_content(new_cves, details):
    branch_order = ["1.1", "3.0", "3.5", "3.6+"]
    branch_cves = {b: [] for b in branch_order}
    for cve in sorted(new_cves):
        d = details.get(cve, {})
        branches = d.get("branches", set())
        if not branches:
            continue
        for b in branches:
            if b in branch_cves:
                branch_cves[b].append(cve)
    lines = [f"新增 {len(new_cves)} 个漏洞:"]
    for b in branch_order:
        if branch_cves[b]:
            lines.append(f"{b}分支：{', '.join(branch_cves[b])}")
    return "\n".join(lines)


def build_mail_content(new_cves, details):
    lines = [f"<h2>OpenSSL 新增漏洞提醒 ({len(new_cves)} 个)</h2>"]
    return "".join(lines)


def send_mail(subject, body):
    # msg = MIMEText(body, 'html', 'utf-8')
    # msg['From'] = CONFIG["smtp_user"]
    # msg['To'] = CONFIG["mail_to"]
    # msg['Subject'] = subject
    # with smtplib.SMTP_SSL(CONFIG["smtp_server"], CONFIG["smtp_port"]) as smtp:
    #     smtp.login(CONFIG["smtp_user"], CONFIG["smtp_pass"])
    #     smtp.sendmail(CONFIG["smtp_user"], [CONFIG["mail_to"]], msg.as_string())
    pass


def main():
    html = fetch_page()
    cve_ids, details = extract_cves(html)
    known = load_known()
    new_cves = cve_ids - known
    if new_cves:
        subject = f"OpenSSL 新增漏洞提醒 ({len(new_cves)} 个)"
        body = build_notify_content(new_cves, details)
        n = Notification("OpenSSL漏洞监控", subject, body, duration="long")
        n.set_audio(audio.Default, loop=False)
        n.show()
        # mail_body = build_mail_content(new_cves, details)
        # send_mail(subject, mail_body)
        print(body)
        print("已发送桌面通知")
    else:
        print("无新增漏洞")
    save_known(cve_ids)


if __name__ == '__main__':
    while(1):
        try:
            main()
            print(datetime.now())
            print("sleep for 1 hour")
            time.sleep(1 * 60 * 60)
        except Exception as e:
            time.sleep(1 * 60 * 60)
