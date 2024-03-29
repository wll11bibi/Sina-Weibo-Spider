基于Scrapy框架的新浪微博爬虫
==========
#### 一个新浪微博的爬虫
a spider of sina weibo
## 2019.9.6 更新说明  
1.重新调整了README.md文件的格式，显得更加美观。    

2.现目前完成了<b>user_info_spider</b>的优化与相应功能的完善。这个爬虫位于spider文件夹下的<b>user_info_spider.py</b>文件之中，其实相应的在该文件夹下还有一个spider名为<b>seed_uid_spider</b>，这个爬虫的功能为通过给定的种子用户uid，即粉丝数量庞大的大V用户，爬取他们的粉丝列表，以此来获得大量用户的uid，进一步通过相应的微博用户信息接口来获取微博用户的详细信息。讲道理最近爬虫的推进陷入了停滞，一个很愚蠢的点在于爬取粉丝列表的同时就可以获取完整的用户信息，根本没有必要将uid写入数据库之后再提前再根据对应的api进行数据采集。但是这样的问题在于会限制以后爬虫的功能扩展，我想的是在完善整个爬虫的构建即可以爬取一个微博用户相应的用户信息、微博内容、微博评论内容之后，提供不同的爬虫工作模式，既可以在给定单个用户uid之后爬取相应的信息，又可以根据用户指定的种子用户爬取其粉丝列表的相关信息。最后<b>user_info_spider</b>与<b>seed_uid_spider</b>这两个爬虫应该会被合并为一个爬虫，根据指定的参数采取不同的爬取模式。    

3.爬取用户微博时，如果用户微博文本过长，需要跳转到另外的一个url才能获取完整的微博内容，这样会导致产生新的额外开销，但目前没有找到解决这样开销的办法。但与此同时，如何判断该用户微博的文本需要跳转"阅读全文"?利用正则匹配精确度不够高，开销也未知难以接受，这个问题还待解决。    

4.开学了，更新速度变慢了，课程作业有点多，但是每周还是会推进项目更新，大创结题压力有点大，说不定后面还得熬熬夜赶一赶。
## 2019.9.3 更新说明
1.重新排版了READM.md文件，虽然还是有点丑，但是会后期继续完善  
~~2.正着手思考解决如何限制爬虫被死锁在一个返回结果为空或者无法爬取到的url的情况~~  
2.新增了对同一url重复爬取次数限制，新增在settings.py文件中的<b>'WEIBO_INFO_SPIDER_REPEAT_TIME'</b>字段中，默认设置为5次。同时新增字段<b>'USER_INFO_SPIDER_SLEEP_TIME'</b> 
即用户可以自行设置收到418状态码时程序的休眠时间，默认为60s    
3.正着手编写具体每一条微博的爬虫爬取，但是发现一个问题。目前针对某一个用户的微博爬取，采取了用户自行设置爬取页数的范围。但如果某一用户的微博数量页数小于爬取页数的区间，将会导致整个爬虫锁死在返回数据为空的url连接上。导致这个情况的原因是，在某些情况下爬取微博的url会返回一个空的json数据，需要重新爬取处理，但此时返回的数据与请求微博用户不存在页数时返回的数据完全一样，导致无法区分究竟是爬取失败还是该页面本来就不存在，正思考如何解决。
## 2019.9.2 更新说明
#### 1.重写了user_info_spider的parse方法，优化了爬虫的爬取速率，减小了内存的开销，利用yield关键字与Request对象实现了迭代爬取。
#### 2.新增了某一URL爬取失败的处理，会根据爬取失败的具体情况重新生成Request对象进行爬取数据。（注：但在更新写readme的时候突然想到没有避免爬虫被锁死在这个url上的情况，即若这个url一直爬不下来，爬虫将会一直爬，这个坑后面填）
#### 3.修改了README.md中的一些bug
## 项目说明
这是一个基于Python Scrapy框架的新浪微博爬虫      
## 项目依赖：  
<em>Python3.7 MySQL5.7  Scrapy 1.5 </em>     
## 项目简介

1.这是一个通用的微博爬虫，目前暂时只实现了微博用户信息采集的功能，具体每一条微博的信息采集正在实现中    

2.速度不够快，跑一个晚上大概也就10000条数据左右，没有实现代理ip，因为穷，所以买不起一天20+的代理ip，而且懒，所以不想自己去慢慢找能活得久一点的代理    

3.本来做这个爬虫是为了大创的数据采集来用，最近刚开学事情不多所以会更新比较频繁，具体每一条微博的采集功能正在逐渐实现    

4.第一次学习使用Scrapy框架，而且也算是第一次正式的用GitHub，前几天写的代码着实太愚蠢，但微博爬虫工作很繁琐，没有时间去修改之前写得太蠢的地方，准备一边继续写一边继续优化    

5.现在大概爬了四万条左右的用户信息数据，主要爬取的网站是 [m.weibo.cn](https://m.weibo.cn) 微博的移动站    

6.相对PC站而言m站更容易获取数据，而且相对而言数据更加工整（ajax请求返回的json数据）更容易被提取出来，不需要进行模拟登陆，所以选择了对m站的数据进行爬取    

7.数据库在我本地建好了已经，但是最近事情还是有点多，其实是我懒，所以我暂时先不把数据库表放上来（这坑以后会填）
  
8.最后说一点数据库，数据的插入用到了Twisted框架，实现了将爬取到的数据异步插入，从而在某种程度上规避了通常意义上的同步插入给爬虫带来的运行阻塞
## 运行项目 

进入项目的目录    

运行 scrapy crawl xxxspider    

爬虫会自动运行爬取数据，但现在可能还暂时跑不了，因为项目前半部分对Scrapy框架还不熟悉就开始写了，着实写得有点蠢

## 项目展望
#### 1. 速度的扩展  
虽然嘴上说着穷，不过还是得把代理给搞定，没有那玩意爬取速度还是太慢了，不过问题不大，主要是没钱（留下了贫穷的泪水）在所有功能完善，bug改完之后，准备租一天的代理把代理给实现了，代理有爬取速度就上去了，说多了都是泪
#### 2. 分布式的展望
完成单机上的爬虫之后，准备实现把这个爬虫扩展为分布式的爬虫，用Scrapy-Redis框架

