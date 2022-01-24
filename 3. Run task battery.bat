if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
@ECHO OFF
call conda activate psytask
python Tasks/mainscript.py
