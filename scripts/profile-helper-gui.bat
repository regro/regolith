@echo off
call :s_which py.exe
if not "%_path%" == "" (
  py -3 -m regolith.helper_gui_main %*
) else (
  python -m regolith.helper_gui_main %*
)

goto :eof

:s_which
  setlocal
  endlocal & set _path=%~$PATH:1
  goto :eof
