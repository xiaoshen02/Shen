#include <stdio.h>
#include <pcap.h>
#include <string.h>
#include <stdlib.h>
#include <arpa/inet.h>

#define SIZE_ETHERNET    14
#define ETHER_ADDR_LEN   6
#define MAXBYTES2CAPTURE 2048

/* 以太网首部 */
struct sniff_ethernet {
    u_char ether_dhost[ETHER_ADDR_LEN];  /* 目的MAC地址 */
    u_char ether_shost[ETHER_ADDR_LEN];  /* 源MAC地址 */
    u_short ether_type;                 /* 后续协议类型 */
};

/* IPv4首部 */
struct sniff_ip {
    u_char ip_vhl;           /* 版本和首部长度 */
    u_char ip_tos;           /* 服务类型 */
    u_short ip_len;          /* 总长度 */
    u_short ip_id;           /* 标识 */
    u_short ip_off;          /* 标志和片偏移 */
    u_char ip_ttl;           /* 生存时间 */
    u_char ip_p;             /* 上层协议 */
    u_short ip_sum;          /* 首部校验和 */
    struct in_addr ip_src, ip_dst;  /* 源、目的IP地址 */
};

/* 提取首部长度，单位为4字节 */
#define IP_HL(ip) (((ip)->ip_vhl) & 0x0f)

/* 提取版本号 */
#define IP_V(ip) (((ip)->ip_vhl) >> 4)

void processPacket(u_char *arg,
                   const struct pcap_pkthdr *pkthdr,
                   const u_char *packet)
{
    int i;
    int *counter = (int *)arg;
    const struct sniff_ethernet *ethernet;
    const struct sniff_ip *ip;
    int version;
    int header_length;
    unsigned int total_length;

    printf("\n---------- 第%d个数据包 ----------\n", ++(*counter));
    printf("原始数据包长度：%u 字节\n", pkthdr->len);
    printf("实际捕获长度：%u 字节\n", pkthdr->caplen);

    if (pkthdr->caplen < SIZE_ETHERNET) {
        printf("以太网首部不完整\n");
        return;
    }

    ethernet = (const struct sniff_ethernet *)packet;

    printf("源MAC地址：");
    for (i = 0; i < ETHER_ADDR_LEN; i++) {
        printf("%02x", (unsigned int)ethernet->ether_shost[i]);

        if (i != ETHER_ADDR_LEN - 1)
            printf(":");
    }
    printf("\n");

    printf("目的MAC地址：");
    for (i = 0; i < ETHER_ADDR_LEN; i++) {
        printf("%02x", (unsigned int)ethernet->ether_dhost[i]);

        if (i != ETHER_ADDR_LEN - 1)
            printf(":");
    }
    printf("\n");

    printf("以太网类型：0x%04x\n",
           (unsigned int)ntohs(ethernet->ether_type));

    if (ntohs(ethernet->ether_type) != 0x0800) {
        printf("不是普通以太网格式的IPv4数据包，跳过IP解析\n");
        return;
    }

    if (pkthdr->caplen < SIZE_ETHERNET + 20) {
        printf("IPv4首部不完整\n");
        return;
    }

    /* 跳过以太网首部，找到IP首部 */
    ip = (const struct sniff_ip *)(packet + SIZE_ETHERNET);

    version = IP_V(ip);
    header_length = IP_HL(ip) * 4;

    if (version != 4 || header_length < 20) {
        printf("IPv4首部格式错误\n");
        return;
    }

    if (pkthdr->caplen <
        SIZE_ETHERNET + (unsigned int)header_length) {
        printf("IPv4首部不完整\n");
        return;
    }

    total_length = ntohs(ip->ip_len);

    if (total_length < (unsigned int)header_length) {
        printf("IPv4总长度错误\n");
        return;
    }

    printf("IP版本：%d\n", version);
    printf("IP首部长度：%d 字节\n", header_length);
    printf("IP总长度：%u 字节\n", total_length);
    printf("标识：%u\n",
           (unsigned int)ntohs(ip->ip_id));
    printf("标志和片偏移：0x%04x\n",
           (unsigned int)ntohs(ip->ip_off));
    printf("生存时间：%u\n", (unsigned int)ip->ip_ttl);
    printf("上层协议编号：%u\n", (unsigned int)ip->ip_p);
    printf("首部校验和：0x%04x\n",
           (unsigned int)ntohs(ip->ip_sum));
    printf("源IP地址：%s\n", inet_ntoa(ip->ip_src));
    printf("目的IP地址：%s\n", inet_ntoa(ip->ip_dst));
}

int main(int argc, char *argv[])
{
    int count = 0;
    int result;
    pcap_t *descr;
    char errbuf[PCAP_ERRBUF_SIZE];
    char *device;

    memset(errbuf, 0, sizeof(errbuf));

    if (argc != 2) {
        fprintf(stderr, "用法：%s 网卡名称\n", argv[0]);
        fprintf(stderr, "示例：%s ens33\n", argv[0]);
        return 1;
    }

    device = argv[1];

    printf("正在打开网卡：%s\n", device);

    descr = pcap_open_live(device, MAXBYTES2CAPTURE,
                          1, 512, errbuf);

    if (descr == NULL) {
        fprintf(stderr, "打开网卡失败：%s\n", errbuf);
        return 1;
    }

    if (pcap_datalink(descr) != DLT_EN10MB) {
        fprintf(stderr, "错误：需要使用以太网格式的接口\n");
        pcap_close(descr);
        return 1;
    }

    /* 抓取5个数据包后停止 */
    result = pcap_loop(descr, 5, processPacket, (u_char *)&count);

    if (result == -1) {
        fprintf(stderr, "抓包失败：%s\n", pcap_geterr(descr));
        pcap_close(descr);
        return 1;
    }

    printf("\n共捕获%d个数据包，抓包结束。\n", count);

    pcap_close(descr);
    return 0;
}