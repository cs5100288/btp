#include <postgresql/libpq-fe.h>
#include <string>
#include <iostream>
#include <fstream>

using namespace std;

int     main(int argc,char* argv[]) {
  PGconn          *conn;
  PGresult        *res;
  if(argc!=2)
  {
    cout<<"Usage : bulkinsert <file-to-read-queries> "<<endl;
    return(1);
  }
  conn = PQconnectdb("dbname=minip-website host=agni.iitd.ac.in user=django-user password=minip2012");

  if (PQstatus(conn) == CONNECTION_BAD) {
    puts("We were unable to connect to the database");
    return (0);
  }
  string line;
  ifstream myfile (argv[1]);
  if (myfile.is_open())
  {
    while ( myfile.good() )
    {
      getline (myfile,line);
      res = PQexec(conn, (char*)line.c_str());
      PQclear(res);
      cout <<"Exec: "<< line << endl;
    }
    myfile.close();
  }
  else cout << "Unable to open file"; 

  PQfinish(conn);

  return 0;
}
