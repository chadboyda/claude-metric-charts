#!/usr/bin/env python3
"""Upload files to Slack as the user (user token from the Slack MCP config), one message. Usage: metric-charts upload <channel> <thread_ts or ""> "<message>" <files...>
Never prints the token."""
import json, os, sys, urllib.parse, urllib.request

cfg = json.load(open(os.path.expanduser('~/.claude.json')))
env = cfg['mcpServers']['slack']['env']
TOKEN, COOKIE = env['SLACK_MCP_XOXC_TOKEN'], env.get('SLACK_MCP_XOXD_TOKEN', '')
HDR = {'Authorization': f'Bearer {TOKEN}', 'User-Agent': 'metric-charts-upload/1.0'}
if COOKIE:
    HDR['Cookie'] = f'd={COOKIE}'


def api(method, data):
    req = urllib.request.Request(f'https://slack.com/api/{method}', data=urllib.parse.urlencode(data).encode(),
                                 headers={**HDR, 'Content-Type': 'application/x-www-form-urlencoded'})
    out = json.load(urllib.request.urlopen(req, timeout=60))
    if not out.get('ok'):
        sys.exit(f'{method} failed: {out.get("error")}')
    return out


channel, thread_ts, message, files = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
ids = []
for path in files:
    size = os.path.getsize(path)
    up = api('files.getUploadURLExternal', {'filename': os.path.basename(path), 'length': size})
    with open(path, 'rb') as f:
        body = f.read()
    urllib.request.urlopen(urllib.request.Request(up['upload_url'], data=body,
                                                  headers={'User-Agent': HDR['User-Agent']}), timeout=120)
    ids.append({'id': up['file_id'], 'title': os.path.basename(path)})
data = {'files': json.dumps(ids), 'channel_id': channel, 'initial_comment': message}
if thread_ts:
    data['thread_ts'] = thread_ts
api('files.completeUploadExternal', data)
print(f'uploaded {len(ids)} file(s) to {channel}')
