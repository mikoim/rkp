var g="",l,m;String.prototype.replaceAll=function(d,k){return this.split(d).join(k)};function n(d,k){var b;$(".pagination").empty();if(0!=d)for(b=1;b<=d/k+1;b++)$(".pagination").append('<li><a href="#'+b+'">'+b+"</a></li>");$(".pagination a").on("click",function(){m=$(this).text();q(!1);event.preventDefault()})}
function q(d){!0==d&&(m=1,l=$("form").serialize());$.ajax({type:"GET",url:"api.php",data:l+"&page="+m,dataType:"json",success:function(d){var b=d.data,p=50*(m-1);$("#lecture").empty();for(var c in b){var a=g;p++;for(var a=a.replaceAll("%a%",p),a=a.replaceAll("%b%",b[c]["\u5e74\u5ea6"]),a=a.replaceAll("%z%",b[c]["\u5b66\u90e8"]),a=a.replaceAll("%c%",b[c]["\u79d1\u76ee\u30b3\u30fc\u30c9"]),a=a.replaceAll("%d%",b[c]["\u958b\u8b1b\u671f\u9593"]),a=a.replaceAll("%e%",b[c]["\u958b\u8b1b\u79d1\u76ee\u540d"]),
a=a.replaceAll("%f%",b[c]["\u30af\u30e9\u30b9"]),a=a.replaceAll("%g%",b[c]["\u62c5\u5f53\u8005"]),a=a.replaceAll("%h%",b[c]["\u767b\u9332\u8005\u6570"]),e=[b[c].A,b[c].B,b[c].C,b[c].D,b[c].F,b[c].Other],h=0,f=0;6>f;f++)if(h+=e[f],100<h){e[f]-=h-100;e[f]=Math.floor(100*e[f])/100;break}a=a.replaceAll("%i0%",e[0]);a=a.replaceAll("%i1%",e[1]);a=a.replaceAll("%i2%",e[2]);a=a.replaceAll("%i3%",e[3]);a=a.replaceAll("%i4%",e[4]);a=a.replaceAll("%i5%",e[5]);a=a.replaceAll("%j%",b[c]["\u8a55\u70b9\u5e73\u5747\u5024"]);
$("#lecture").append(a)}n(d.info.total,d.info.limit)},error:function(){alert("Can't connect to the server.")},complete:function(){}})}$(function(){null!=/(MSIE|Trident)/.exec(window.navigator.userAgent)&&$("#ieWarning").modal(options);$("form").submit(function(d){q(!0);d.preventDefault()});g=$("#lecture").html();q(!0)});