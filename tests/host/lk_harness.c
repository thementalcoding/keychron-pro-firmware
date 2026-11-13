/* Host-side harness: runs the real lkbt51_read()/lkbt51_task() parser against a fake transport under ASan/UBSan.
 * Built by tests/host/run_host_tests.sh; see that script for usage. */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#define PACKET_MAX_LEN 64
#define HAL_USE_SPI 1
#define LKBT51_INT_INPUT_PIN 1
typedef struct { int x; } SPIDriver; static SPIDriver WT_DRIVER; static int spicfg;
static uint8_t module_resp[128]; static int int_low=0;
static void spiStart(SPIDriver*d,void*c){(void)d;(void)c;} static void spiSelect(SPIDriver*d){(void)d;} static void spiUnselect(SPIDriver*d){(void)d;} static void spiStop(SPIDriver*d){(void)d;}
static volatile uint8_t sink;
static void spiExchange(SPIDriver*d,int n,const void*tx,void*rx){ (void)d; const uint8_t*t=tx; uint8_t*r=rx; for(int i=0;i<n;i++){ sink=t[i]; r[i]=module_resp[i]; } }
static int gpio_read_pin(int p){ (void)p; if(int_low){int_low--; return 0;} return 1; }
static uint8_t expect_len=64; static uint32_t factory_reset=0; static uint32_t timer_read32(void){return 1;} static uint32_t timer_elapsed32(uint32_t t){(void)t;return 1;}
typedef struct { int evt_type; int data; union { int hostIndex; int reason; int led; int interval; } params; } wireless_event_t;
enum {EVT_RESET=1,EVT_CONNECTED,EVT_DISCOVERABLE,EVT_RECONNECTING,EVT_DISCONNECTED,EVT_BT_PINCODE_ENTRY,EVT_EXIT_BT_PINCODE_ENTRY,EVT_SLEEP,EVT_HID_INDICATOR,EVT_CONECTION_INTERVAL};
enum {LKBT51_CONNECTED=0x20,LKBT51_DISCOVERABLE,LKBT51_RECONNECTING,LKBT51_DISCONNECTED,LKBT51_PINCODE_ENTRY,LKBT51_EXIT_PINCODE_ENTRY,LKBT51_SLEEP};
enum {LK_EVT_MSK_CONNECTION=1,LK_EVT_MSK_LED=2,LK_EVT_MSK_BATT=4,LK_EVT_MSK_RESET=8,LK_EVT_MSK_RPT_INTERVAL=16};
static void wireless_event_enqueue(wireless_event_t e){(void)e;} static void lkbt51_send_conn_evt_ack(void){} static void battery_calculate_voltage(bool a,int v){(void)a;(void)v;}
#define kc_printf(...) do{}while(0)
static uint16_t connection_interval;
static int pkts=0; static void lkbt51_event_handler(uint8_t evt,uint8_t*d,uint8_t len,uint8_t sn){(void)evt;(void)d;(void)len;(void)sn; pkts++;}
#include INC
static void put_pkt(int at,uint8_t evt){ uint8_t len=5; module_resp[at]=0xAA; module_resp[at+1]=0x57; module_resp[at+2]=len; module_resp[at+3]=~len; module_resp[at+4]=1; uint16_t c=0; uint8_t p[3]={evt,0x11,0}; for(int i=0;i<3;i++){module_resp[at+5+i]=p[i]; c+=p[i];} module_resp[at+8]=c&0xff; module_resp[at+9]=c>>8; }
int main(int argc,char**argv){ int t=atoi(argv[1]);
  if(t==1){ memset(module_resp,0,sizeof module_resp); put_pkt(14,0xA1); int_low=1; lkbt51_task(); printf("L1 normal read (expect_len=64): packets=%d expected=1\n",pkts); }
  if(t==2){ memset(module_resp,0,sizeof module_resp); module_resp[14]=0xAA; module_resp[15]=0x57; module_resp[16]=100; module_resp[17]=(uint8_t)~100; int_low=1; lkbt51_task(); memset(module_resp,0,sizeof module_resp); for(int k=0;k<5;k++){ put_pkt(14,0xA1); int_low=1; lkbt51_task(); } printf("L2 header len=100 then 5 valid ACKs: packets=%d expected=5\n",pkts); }
  if(t==3){ memset(module_resp,0,sizeof module_resp); module_resp[50]=0xAA; module_resp[51]=0x57; module_resp[52]=50; module_resp[53]=(uint8_t)~50; int_low=1; lkbt51_task(); printf("L3 header at i=50 with len=50: packets=%d expected=0\n",pkts); }
  return 0; }
