import glob

files = glob.glob('web/*.html')
for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    new_content = content
    # replace unversioned brand links
    new_content = new_content.replace('/brand/logo-light.svg"', '/brand/logo-light.svg?v=shinecut3"')
    new_content = new_content.replace('/brand/logo.svg"', '/brand/logo.svg?v=shinecut3"')
    new_content = new_content.replace('/brand/favicon.svg"', '/brand/favicon.svg?v=shinecut3"')
    if new_content != content:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print('Updated', fpath)
