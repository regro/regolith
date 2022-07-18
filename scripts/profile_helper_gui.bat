@echo off
call :s_which py.exe
if not "%_path%" == "" (
  py -3 -m profile_helper_gui %*
) else (
  python -m profile_helper_gui %*
)

goto :eof

:s_which
  setlocal
  endlocal & set _path=%~$PATH:1
  goto :eof