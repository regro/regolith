$PROJECT = 'regolith'
$ACTIVITIES = ['version_bump', 'changelog', 'tag', 'conda_forge', 'ghrelease']

$VERSION_BUMP_PATTERNS = [
    ('regolith/__init__.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
    ('setup.py', '        version\s*=.*,', "        version='$VERSION',")
    ]
$CHANGELOG_FILENAME = 'CHANGELOG.rst'
$CHANGELOG_IGNORE = ['TEMPLATE.rst']
$TAG_REMOTE = 'git@github.com:regro/regolith.git'

$GITHUB_ORG = 'regro'
$GITHUB_REPO = 'regolith'
