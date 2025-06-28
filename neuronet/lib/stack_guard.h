#pragma once

unsigned long __stack_chk_guard;
void __stack_chk_guard_setup(void);
void __stack_chk_fail(void);
