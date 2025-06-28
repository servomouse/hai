#include "stack_guard.h"

void __stack_chk_guard_setup(void)
{
     __stack_chk_guard = 0xBAAAAAAD;    //provide some magic numbers
}

void __stack_chk_fail(void)
{
    printf("Stack corrupted!\n");
    exit(EXIT_FAILURE);                                
}