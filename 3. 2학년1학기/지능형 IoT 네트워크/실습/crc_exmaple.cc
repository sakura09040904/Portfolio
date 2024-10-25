/* CRC-32b version 1.03 by Craig Bruce, 27-Jan-94
**
** Based on "File Verification Using CRC" by M ark R. Nelson in Dr. Dobb's ** Journal, M ay 1992, pp. 64-67. This program DOES generate the same CRC **  values as ZM ODEM and PKZIP
**
**   
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <time.h>
#include <math.h>
#define OCTET       256
#define ECTET_MAX    255
#define FRAME_SIZE  1024
#define FCS_SIZE     4
#define TOTAL_SIZE  1028
#define ERROR_STEP  200
#define ERROR_MAX  4100
#define TEST_TIMES  1000

void frame_gen(char *frame) ;
void error_gen(char *frame, int err_cnt) ; void crcgen(void) ;
void err_pos_gen(int err_cnt) ;
int get_fcs(char *frame, int frame_size) ;

unsigned long crcTable[256]; 
int error_pos[TOTAL_SIZE*8] ;

/****************************************************************************/ 
int main( int argc, char *argv[] )
{
    int err_cnt, i, count ;
    unsigned long crc;
    time_t seed ;
    char in_frame[TOTAL_SIZE], out_frame[TOTAL_SIZE] ;
    time(&seed) ;
    srand(seed) ;
    crcgen(); /* 초기화... */

    printf("  *** CRC 에러 검출 시뮬레이션 ***\n\n") ;
    printf("에러수\t\t전송수\t\t검출수\n") ;
    for(err_cnt=ERROR_STEP ; err_cnt<ERROR_MAX ; err_cnt+=ERROR_STEP) 
    /* 시뮬레이션을 에러가 1개일때 6개 일때 11개일때... 31개일때 */
    {
        count = 0 ;
        err_pos_gen(err_cnt) ;
        /* 에러가 발생할 자리를 미리 정한다.*/
        for(i=0 ; i<TEST_TIMES ; i++)
        {
            frame_gen(in_frame) ;
            crc = get_fcs(in_frame, FRAME_SIZE) ; 
            memcpy(in_frame+FRAME_SIZE, &crc, sizeof(crc)) ; 
            memcpy(out_frame, in_frame, TOTAL_SIZE) ;
            error_gen(out_frame, err_cnt) ;
            crc = get_fcs(out_frame, TOTAL_SIZE) ;
            if(crc != 0) count ++ ;
        }
        printf("%5d\t\t%5d\t\t%5d\n", err_cnt, i, count) ;
    }
    return( 0 );
}
/****************************************************************************/ 
/* void frame_gen(char *frame) ;                                         */ 
/*      쓰임새 : 난수발생으로 임의의 데이터 전송 프레임을 만든다.           */
/*      매개변수 :                                                          */ 
/*              frame - 난수 발생으로 생성한 데이터 프레임이 저장될 주소    */ 
/*      반환값 : 없음.                                                      */
/****************************************************************************/ 

void frame_gen(char *frame)
{
    int i ;
    for(i=0 ; i<FRAME_SIZE ; i++)
    frame[i] = rand()%255 ;
    /* 0-255 사이의 난수 발생 */
}
/****************************************************************************/ /*    void error_gen(char *frame, int err_cnt) ;                            */
/*      쓰임새 : 난수발생으로 임의의 에러를 생성한다.                       */
/*      매개변수 :                                                          */ /*              frame - 데이터 프레임이 저장되어 있는 주소                  */
/*              err_cnt - 데이터 프레임에서 발생할 에러의 개수              */ /*      반환값 : 없음.                                                      */
/****************************************************************************/ 
void error_gen(char *frame, int err_cnt)
{
    int i=0, l, k ;
    for(i=0 ; i<err_cnt ; i++)
    {
        l = error_pos[i]/ 8 ;
        k = error_pos[i]%8 ;
        frame[l] = frame[l] ^ (1<<k) ;
    }
        /* 미리 결정한 에러가 발생할 자리의 비트를 반전시켜서 에러를 발생시킨다. */
}
/****************************************************************************/ 
/*    void err_pos_gen(int err_cnt) ;                                       */
/*      쓰임새 : 에러가 발생할 위치를 미리 결정해 놓는다.                   */
/*              속도문제 개선을 위해 미리 계산해 놓는다.                    */ 
/*      매개변수 :                                                          */ 
/*              err_cnt - 에러가 발생할 개수                                */ 
/*      반환값 : 없음.                                                      */
/****************************************************************************/ 
void err_pos_gen(int err_cnt)
{
    int i, j, k ;
    for(i=0 ; i<err_cnt ; i++)
    {
        while(j!=i)
        {
            k = rand()%(TOTAL_SIZE*8);
            for(j=0 ; j<i ; j++)
            {
                if(error_pos[j]==k) break;
            }
            error_pos[i] = k ;
        }
    }
}

/****************************************************************************/ 
/*    void crcgen(void) ;                                                   */ 
/*      쓰임새 : 바이트(256개)에 대한 CRC-32에 대한 나머지값들을 계산과정   */ 
/*              에서의 속도문제 개선을 위해 미리 계산해 놓는다.             */ 
/*      매개변수 : 없음.                                                    */ 
/*      반환값 : 없음.                                                      */
/****************************************************************************/ 
void crcgen(void)
{
    unsigned long crc, poly;
    int i, j;
    poly = 0xEDB88320L; /* z modem과 pkz ip에서 사용되는 공개 폴리노미얼 */
    for (i=0; i<256; i++) 
    {
        crc = i;
        for (j=8; j>0; j--) 
        {
            if (crc&1) 
            {
                crc = (crc >> 1) ^ poly; /* 1이면, 뺀다.*/
            } 
            else 
            {
                crc >>= 1; /* 0이면, 쉬프트만 */
            }
        }
        crcTable[i] = crc;
    } /* 8비트(256)에 해당하는 CRC의 나머지 값을 미리 계산해 놓는다. */
     /* 최하위 비트가 그림에서의 최상위 비트가 된다. (역순으로 계산함...) */
}
/****************************************************************************/ 
/*    void get_fcs(char *frame, int frame_siz e) ;                           */ 
/*      쓰임새 : 현재 프레임에 대한 FCS값(CRC 검사값)을 얻어온다.           */ 
/*      매개변수 :                                                          */ 
/*              frame - CRC를 check할 데이터 프레임.                        */ 
/*              frame_siz e - 데이터 프레임의 크기.                          */ 
/*      반환값 : 없음.                                                      */
/****************************************************************************/ 
int get_fcs(char *frame, int frame_size)
{
    register unsigned long crc ;
    int i ;
    crc = 0xFFFFFFFF;
    /* 데이터 프레임 전체를 하나의 M 으로 보고 FCS를 계산한다. */
    for(i=0 ; i<frame_size ; i++)
    {
        crc = ((crc>>8) & 0x00FFFFFF) ^ crcTable[(crc^frame[i]) & 0xFF]; 
    } /* 들어온 바이트 만큼 쉬프트 시키면서 나머지를 계산해 나간다. */
    return (crc^0xFFFFFFFF) ;  /* 처음에 반전된 것을 원래대로 만든다. */
}