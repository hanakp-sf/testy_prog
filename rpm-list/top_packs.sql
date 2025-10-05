-- select pro_name, count(*) from provides group by pro_name having count(*) > 1;
--select * from provides where pro_name = 'atk-lang';
--select * from requires;
select distinct pkg_name, pkg_size/1024/1024 as pkg_size_mb,pkg_size from provides where pkg_name not in 
(select distinct b.pkg_name from requires a inner join provides b on a.req_name = b.pro_name)
order by pkg_size desc; 