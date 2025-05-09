# Kimchi premium for KRX gold prices

![](./data/kimchi_gold_price_recent_12months.png)

The script calculates the Kimchi premium for KRX gold prices.

# 리눅스 서버에서 매일 자동 실행

## 크론탭 등록 예시
터미널에서 아래 명령어로 크론탭 편집:

```text
crontab -e
```

매일 오전 9시에 실행하려면 아래 줄을 추가:

```text
0 9 * * * /usr/bin/python3 /path/to/collect_price.py
```

- `/usr/bin/python3` 경로는 `which python`로 확인
- `/path/to/collect_price.py`는 실제 파일 경로로 변경
- gold_price_log.csv 파일에 날짜별로 데이터가 누적 저장됩니다.
- 크론탭 로그 등은 필요에 따라 별도 설정 가능합니다.
- 에러 발생 시 메시지가 출력됩니다.

# References

- https://blog.stephenturner.us/p/uv-part-2-building-and-publishing-packages
- https://ecos.bok.or.kr/api/#/DevGuide/StatisticalCodeSearch
- https://docs.outcode.biz/tutorials/api/gold
- http://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201060201
