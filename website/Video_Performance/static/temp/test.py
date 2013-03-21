import csv, os, subprocess, time
with open('test.csv') as test:
    with open('op.csv', 'w') as op_file:
        writer = csv.writer(op_file)
        reader = csv.reader(test)
        for row in reader:
            ip, urls = row
            urls = urls.split("::")[:-1]
            print ip, urls
            #p = subprocess.Popen("ping %s -t -n 4" % ip, stdout=subprocess.PIPE, shell=True)
            cmd = "ping -c 4 %s | tail -1 | awk '{print $4}' | cut -d '/' -f 2" % ip
            print cmd
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            pingTime = -1
            try:
                op = p.stdout.read()
                print op
                #op = op[op.find("Average = ") + 10:]
                #op = op[:op.find("ms")]
                pingTime = float(op)  # ms
            except Exception as e:
                print "cannot ping %s" % ip
            for url in urls:
                q = subprocess.Popen("wget --no-cache --no-dns-cache -qO- %s > /dev/null" % url, stdout=subprocess.PIPE, shell=True)
                q.stdout.read()
                time.sleep(2)
            writer.writerow([row[0], pingTime, row[1]])
