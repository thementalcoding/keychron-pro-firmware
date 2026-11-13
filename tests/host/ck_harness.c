/* Host-side harness: runs the real ckbt51_task() parser against a fake transport under ASan/UBSan.
 * Built by tests/host/run_host_tests.sh; see that script for usage. */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#define PACKECT_HEADER_LEN 5
#define PACKET_MAX_LEN 64
#define TIME_IMMEDIATE 0
#define dprintf(...) ((void)0)
static uint16_t checksum_errors;
static uint8_t q[4096]; static int qh=0, qt=0;
struct { struct { int q_counter; } iqueue; } WT_DRIVER;
static void push(const uint8_t*b,int n){ for(int i=0;i<n;i++) q[qt++]=b[i]; WT_DRIVER.iqueue.q_counter=qt-qh; }
static int sdGet(void*d){ (void)d; if(qh==qt) return -1; int v=q[qh++]; WT_DRIVER.iqueue.q_counter=qt-qh; return v; }
static int sdGetTimeout(void*d,int t){ (void)t; return sdGet(d); }
static uint32_t now=0; static uint32_t timer_read32(void){return now;} static uint32_t timer_elapsed32(uint32_t t){return now-t;}
static int events=0, last_evt=-1;
static void ckbt51_event_handler(uint8_t evt, uint8_t*data, uint8_t len, uint8_t sn){ (void)data;(void)len;(void)sn; events++; last_evt=evt; }
#include INC
static void wake_reset(void){ WAKE_RESET; }
static void frame(uint8_t evt,const uint8_t*p,int n,uint8_t sn){ uint8_t b[80]; int i=0; uint8_t len=n+3; b[i++]=0xAA;b[i++]=0x57;b[i++]=len;b[i++]=~len;b[i++]=sn; uint16_t c=evt; b[i++]=evt; for(int k=0;k<n;k++){b[i++]=p[k];c+=p[k];} b[i++]=c&0xff;b[i++]=c>>8; push(b,i);}
static void run(int n){ for(int i=0;i<n;i++){ ckbt51_task(); now++; } }
int main(int argc,char**argv){
  int t=atoi(argv[1]); uint8_t ack[3]={0x11,0x00,0x00}; uint8_t conn[3]={0x23,0x00,0x01};
  if(t==1){ frame(0xA1,ack,2,1); run(5); printf("T1 normal frame: events=%d expected=1\n",events); }
  if(t==2){ uint8_t bad[5]={0xAA,0x57,200,(uint8_t)~200,9}; push(bad,5); run(5); for(int k=0;k<5;k++){ frame(0xB3,conn,3,2+k); run(30);} printf("T2 header len=200 then 5 valid frames: events=%d expected=5\n",events); }
  if(t==3){ uint8_t bad[5]={0xAA,0x57,40,(uint8_t)~40,9}; push(bad,5); uint8_t junk[40]={0}; push(junk,40); run(5); /* 40 zero bytes are a well-formed frame (checksum 0): one event, no overflow */ printf("T3 header len=40 (+40 bytes): events=%d expected=1\n",events); }
  if(t==4){ uint8_t part[7]={0xAA,0x57,6,(uint8_t)~6,3,0xB3,0x23}; push(part,7); run(40); frame(0xB3,conn,3,4); run(30); printf("T4 truncated frame + 40 ms + valid frame: events=%d expected=1\n",events); }
  if(t==6){ uint8_t part[7]={0xAA,0x57,6,(uint8_t)~6,3,0xB3,0x23}; push(part,7); run(1); /* STOP1: UART queue re-initialised by sdInit() */ qh=qt; WT_DRIVER.iqueue.q_counter=0; wake_reset(); frame(0xB3,conn,3,4); run(5); printf("T6 STOP1 mid-frame + valid frame after wake: events=%d expected=1\n",events); }
  if(t==5){ uint8_t bad[5]={0xAA,0x57,1,(uint8_t)~1,9}; push(bad,5); uint8_t z[1]={0}; push(z,1); run(5); printf("T5 header len=1: events=%d expected=0\n",events); }
  return 0;
}
