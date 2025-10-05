bool parse( char * v1, char* v2)
{
	
	while ( isspace(getchar()) && !koniec() ) ;
	if (koniec())
	    return false;
	s = getchar();
	if (isidentifikatordelimiter(s)) {
		s=getchar()
		while (!isidentifikatordelimiter(s) && !koniec()) {
			v1.add(s);
			s = getchar();
		}
	    if (koniec())
	        return false;		
	} else {
		s=getchar()
		while (!isidentifikatordelimiter(s) && !isschemadelimiter(s) && !koniec()) {
			v1.add(s);
			s = getchar();
		}
        if (isidentifikatordelimiter(s))
            return false;
	    if (koniec())
	        return true;            
	}
	if (!isschemadelimiter(s))
	    return false;
	s = getchar();
	if (isidentifikatordelimiter(s)) {
		s=getchar()
		while (!isidentifikatordelimiter(s) && !koniec()) {
			v2.add(s);
			s = getchar();
		}
	    if (koniec())
	        return false;		
	} else {
		s=getchar()
		while (!isidentifikatordelimiter(s) && !isschemadelimiter(s) && !koniec()) {
			v1.add(s);
			s = getchar();
		}
        if (isidentifikatordelimiter(s))
            return false;
	    if (koniec())
	        return true;            
	}	
}
