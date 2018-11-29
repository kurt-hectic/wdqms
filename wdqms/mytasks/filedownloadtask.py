import logging
import sys,os
import datetime
import subprocess
from django.conf import settings



class FileDownloadTask:
    # TODO: count number of downloaded files

    WGETCMD = "wget --tries=1 --mirror"


    def __init__(self):
        self.log = logging.getLogger(__name__)
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        out_hdlr.setLevel(logging.INFO)
        self.log.addHandler(out_hdlr)
        self.log.setLevel(logging.INFO)

        self.nrdownloaded = 0

    def run(self):
        self.downloadFiles()

    def downloadFiles(self):

        starttime = datetime.datetime.now()

        importcfg = settings.WDQMS['IMPORTER'] 

        basepath=importcfg['PATH']

        os.chdir(basepath)

        jma_days_back = int(importcfg["JMA_BACK"]  )
        ncep_days_back = int(importcfg["NCEP_BACK"] )
        ecmwf_days_back = int(importcfg["ECMWF_BACK"] )
        dwd_days_back = int(importcfg["DWD_BACK"] )

        self.log.info("start update cycle: {}".format( starttime ))

        base = datetime.datetime.today()

        # do JMA
        date_list = [base - datetime.timedelta(days=x) for x in range(0, jma_days_back)]

        for date in date_list:
           for period in ("00","06","12","18"):
              for mytype in ("SYNOP","TEMP"):
                 path="http://{}:{}@qc.kishou.go.jp/WIGOS_QM/{}/JMA_{}_{}_{}.csv.gz".format( importcfg["USER_JMA"], importcfg["PASSWORD_JMA"], date.strftime("%Y%m"), mytype, date.strftime("%Y%m%d"), period  )
                 self.downloadFile(path)

        #do NCEP
        date_list = [base - datetime.timedelta(days=x) for x in range(0, ncep_days_back)]

        for date in date_list:
           #http://www.emc.ncep.noaa.gov/mmab/WIGOS/ncepdemo_20150911_t00z.csv
           for period in ("00","06","12","18"):
              filename="ncepdemo_{}_t{}z.csv".format( date.strftime("%Y%m%d"), period  )
              path="http://www.emc.ncep.noaa.gov/mmab/WIGOS/" + filename
              self.downloadFile(path)

        # for NCEP we locally compress the files.. but we should keep some uncompressed so that wget can know the real size of the file (to avoid double download)
        date_list = [base - datetime.timedelta(days=x) for x in range(0, ncep_days_back)]
        last_files = []
        for date in date_list:
           for period in ("00","06","12","18"):
              last_files.append("ncepdemo_{}_t{}z.csv".format( date.strftime("%Y%m%d"), period  ))

        for root, dirs, files in os.walk(basepath+"/www.emc.ncep.noaa.gov/mmab/WIGOS/"):
           mypath = root.split('/')
           files = [ fi for fi in files if not fi.endswith( ".csv.gz")  ]
           files = [ fi for fi in files if not fi.endswith( tuple(last_files)  )  ]
           for file in files:
              file = os.path.join(root,file)
              cmd="gzip -q {}".format(file)
              os.system(cmd)


        # do ECMWF
        date_list = [base - datetime.timedelta(days=x) for x in range(0, ecmwf_days_back)]

        for date in date_list:
           for period in ("00","06","12","18"):
              for mytype in ("SYNOP","TEMP"):
                 #ftp://wmodatamon@dissemination.ecmwf.int/ECMF/SYNOP/06/ECMF_SYNOP_20170714_06.csv
                 path="ftp://{}:{}@dissemination.ecmwf.int/ECMF/{}/{}/ECMF_{}_{}_{}.csv".format( importcfg["USER_ECMWF"], importcfg["PASSWORD_ECMWF"], mytype, period, mytype, date.strftime("%Y%m%d"),  period  )
                 self.downloadFile(path)


        # do DWD
        date_list = [base - datetime.timedelta(days=x) for x in range(0, dwd_days_back)]

        for date in date_list:
           for period in ("00","03","06","09","12","15","18","21"):
              for mytype in ("SYNOP",):
                 #ftp://wmodatamon@dissemination.ecmwf.int/ECMF/SYNOP/06/ECMF_SYNOP_20170714_06.csv
                 path="ftp://{}:{}@dissemination.ecmwf.int/DWD/{}/{}/DWD_{}_{}_{}.csv".format( importcfg["USER_ECMWF"], importcfg["PASSWORD_ECMWF"], mytype, period, mytype, date.strftime("%Y%m%d"),  period  )
                 self.downloadFile(path)

        # DWD postprocessing.. we have 3h intervals for DWD
        dwddir="{}/{}".format(basepath, importcfg["DWD_DIR"])
        newdwddir="{}/{}".format(basepath,importcfg["DWD_NEW_DIR"])

        for period in range(0,24,6):
           odir = "{:02d}".format(period + 3)
           mdir = "{:02d}".format(period)

           for file in os.listdir( "{}/{}/".format(dwddir,mdir) ):
              path = "{}/{}/{}".format(dwddir,mdir,file)
              ofile = "{}".format(file).replace("_{}".format(mdir),"_{}".format(odir))
              opath = "{}/{}/{}".format(dwddir,odir,ofile)

              if file.endswith(".csv") and os.path.isfile( opath ): # file exists and has its corresponding file
                 newgzfile = "{}/{}/{}.gz".format(newdwddir,mdir,file)
                 newdir = "{}/{}/".format(newdwddir,mdir)
                 if not os.path.isdir(newdir):
                    self.log.warning("creating {}".format(newdir))
                    os.makedirs(newdir)

                 if not os.path.isfile(newgzfile):
                    with gzip.open(newgzfile,"wb") as gf:
                       gf.write( open(path,"rb").read() )
                       gf.writelines( line.encode("ascii") for line in open(opath) if not line.startswith("#")  )
                   

        endtime = datetime.datetime.now()
        self.log.info("end update cycle: {} , duration:{}, nr: {}".format( endtime, (endtime - starttime).seconds , self.nrdownloaded))

    def downloadFile(self,path):
       
       cmd = "{} {}".format(self.WGETCMD,path)

       try:
          p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,bufsize=1000, universal_newlines=True)
          out,err = p.communicate()
       
          erroroutput=[]
          output=[]
          for line in out:
             output.append(str(line))
          for line in err:
             erroroutput.append(str(line))
       
          code = p.returncode
          errorout = "".join(erroroutput)
       
          if not code and not "Server file no newer than local file" in errorout and not "Remote file no newer than local file" in errorout:
             self.log.info("downloaded: {}".format(path))
             self.nrdownloaded+=1 
             return True
          else:
             return False
       
       
       except subprocess.CalledProcessError as exc:
          self.log.error("error: {}".format(exec))
          return False

    def nrdownloaded(self):
        return self.nrdownloaded
