$PROJECT = 'regolith'
$ACTIVITIES = ['version_bump', 'changelog', 'tag', 'push_tag', 'ghrelease', 'conda_forge']

$VERSION_BUMP_PATTERNS = [
    ('regolith/__init__.py', '__version__\s*=.*', "__version__ = '$VERSION'"),
    ('setup.py', 'version\s*=.*,', "version='$VERSION',")
    ]
$CHANGELOG_FILENAME = 'CHANGELOG.rst'
$CHANGELOG_IGNORE = ['TEMPLATE.rst']
$PUSH_TAG_REMOTE = 'git@github.com:regro/regolith.git'

$GITHUB_ORG = 'regro'
$GITHUB_REPO = 'regolith'
$GHRELEASE_TARGET = 'b839663f04377f1a25fb864d0764f7d2aabd991a'