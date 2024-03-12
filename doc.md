# bot架构
## 登入
需要在config.cfg的[bot]中填入对应的id和令牌  
## 使用
### 查询bot是否在线
```
/ping 
```
### 绑定和解绑konamiID
```
/konami bind [ID]
/konami unbind
```
### 使用konamiID查询sdvx分数
查询best 50  
```
/sdvx b50
```
查询最新游玩歌曲的最佳记录
```
/sdvx pr
```
查询特定难度的点灯信息
```
/sdvx sm [难度]
```
### 绑定和解绑aimeID
```
/aime bind [ID]
/aime unbind
```
### 使用aimeID查询ongeki分数
查询用户信息
```
/ongeki user
```
查询最近游玩记录
```
/ongeki pr
```
查询b30数据
```
/ongeki bp
```
### 使用aimeID查询chuniv2分数
查询用户信息
```
/chuni user
```
查询最近游玩记录
```
/chuni pr
```
查询b30数据
```
/chuni bp
```
### 函数外的互动
包含下面字符即可触发，优先级从上到下
```
程序状态
硬件状态
服务状态
软件声明
最近怎么样
摸摸
-仅@-
```