-- zo vsetkych > ako cca 100 MB
select distinct pkg_name, pkg_size/1024/1024 as pkg_size_mb,pkg_size from provides where pkg_size > 100000000
order by pkg_size desc; 