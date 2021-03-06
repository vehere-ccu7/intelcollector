# -*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup


class FeedCollector(object):    
    def __init__(self, url, feed_name, category=None):
        self.url = url
        self.name = feed_name
        self.category = category
        self.raw_folder = ""
        self.indicator_types = []

    def download_raw_files(self, path):
        os.system("wget "+self.url+" -P "+path+"/"+self.name)
        self.raw_folder = path +"/"+self.name

    def set_ioc_types(self, ioc_type):
        self.indicator_types = ioc_type

    def merge_values(self, file_path, target_file_path):  
        pass

    def append_values(self, target_file_path, new_lines):
        new_lines = list(set(new_lines))
        l = len(new_lines)
        c = 0
        if not os.path.exists(target_file_path+".txt"):        
            pass
        else:
            old_f = open(target_file_path+".txt", "r")
            old_values = old_f.readlines()
            old_f.close()
            l = len(old_values)
            new_lines = list(set(new_lines+old_values))
        new_f = open(target_file_path+".txt", "w")
        new_f.writelines(new_lines)
        new_f.close()
            
    def extract_values(self, raw_folder_path, target_file_path, ioc_type):
        self.files_list = os.listdir(raw_folder_path)
        for file_name in self.files_list:
            self.merge_values(raw_folder_path+"/"+file_name, target_file_path, ioc_type)


class DantorCollector(FeedCollector):    
    def __init__(self, url, feed_name):
        super(DantorCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["tor"])

    def download_raw_files(self, path):
        for url in self.url:
            os.system("wget "+url+" -P "+path+"/"+self.name)
        self.raw_folder = path +"/"+self.name

    def merge_values(self, file_path, target_file_path):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        self.append_values(target_file_path, lines)


class DomainCollector(FeedCollector):
    def __init__(self, url, feed_name):
        super(DomainCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["domain"])

    def merge_values(self, file_path, target_file_path, ioc_type):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        self.append_values(target_file_path, lines[1:])


class FeodoCollector(FeedCollector): 
    def __init__(self, url, feed_name):
        super(FeodoCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["bot"])

    def download_raw_files(self, path):
        for url in self.url:
            os.system("wget "+url+" -P "+path+"/"+self.name)
        self.raw_folder = path +"/"+self.name

    def merge_values(self, file_path, target_file_path, ioc_type):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        new_lines = []
        for line in lines:
            if not "#" in line and not "," in line:
                new_lines.append(line)
            if "," in line:
                new_lines.append(line.split(",")[1][1:-1]+"\n")
        self.append_values(target_file_path, new_lines)


class FireholCollector(FeedCollector):
    def __init__(self, url, feed_name):
        super(FireholCollector, self).__init__(url, feed_name)

        self.set_ioc_types(["bot", "tor", "blacklist"])

    def download_rep(self, url):
        os.system("git clone "+url+" temp/")
 
    def download_raw_files(self, path):
        cwd = os.getcwd()
        self.download_rep(self.url)
        self.move_lists(path, cwd+"/temp")
        os.system("rm -r "+cwd+"/temp/")

    def download_raw_files(self, path):
        cwd = os.getcwd()
        self.download_rep(self.url)
        self.move_lists(path, cwd+"/temp")
        os.system("rm -r "+cwd+"/temp/")

    def move(self, copy_location, paste_location):
        os.system("cp "+copy_location+" "+paste_location+"/"+self.name)

    def move_lists(self, folder_path, git_path):
        cues = "blocklist cleantalk dronebl firehol_abusers ipblocklist stopforspam sblam proxylists proxy ri_connect ri_web " \
           "socks_proxy ssl_proxy xroxy bi_any bi_apache bi_as bi_cms bi_default bi_dns bi_dov bi_ftp bi_htt bi_mail bi_ " \
           "blocklist_de blueliv dataplane dshield_ firehol_ normshield_ urandomusto".split(" ")
        files_list = os.listdir(git_path)
        os.system("mkdir "+folder_path+"/"+self.name)
        for file_name in files_list:
            complete_path = git_path+"/"+file_name
            if os.path.isfile(complete_path):
                for cue in cues:
                    if cue in file_name and "bot" and "dos" and "tor" not in file_name:
                        self.move(complete_path, folder_path)
                        break
                    elif "bot" in file_name:
                        self.move(complete_path, folder_path)
                        break
                    elif "dos" in file_name:
                        self.move(complete_path, folder_path)
                        break
                    elif "tor" in file_name:
                        self.move(complete_path, folder_path)
                        break
    def get_ips(self, subnet):
        def getNext(ip_arr):
            i = 3
            while i > 0:
                if ip_arr[i] == 255:
                    ip_arr[i] = 0
                    i -= 1
                else:
                    ip_arr[i] += 1
                    break      
            return ip_arr 
        subnet_arr = subnet.split("/")
        root_ip, size = subnet_arr[0].split('.'), 2**(32 - int(subnet_arr[1]))
        root = [int(root_ip[i]) for i in range(len(root_ip))]
        ips = []
        for i in range(size):
            ips.append(root.copy())
            root = getNext(root)
        res = []
        for ip in ips:
            temp = ".".join([str(ip[j]) for j in range(len(ip))])
            res.append(temp+"\n")
        return res
                
    def merge_values(self, file_path, target_file_path, ioc_type):
        if ioc_type in file_path:
            f = open(file_path, "r")
            lines = f.readlines()
            new_lines = []
            for line in lines:
                if not "#" in line:
                    if '/' not in line:
                        new_lines.append(line)
                    else:
                        for ip in self.get_ips(line):
                            new_lines.append(ip)
            self.append_values(target_file_path, new_lines)

            

class GreenSnowCollector(FeedCollector):
    def __init__(self, url, feed_name):
        super(GreenSnowCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["blacklist"])
    
    def merge_values(self, file_path, target_file_path, ioc_type):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        self.append_values(target_file_path, lines[1:])


class MalshareCollector(FeedCollector): 
    def __init__(self, url, feed_name):
        super(MalshareCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["hashes"])


class MISPCollector(FeedCollector):  
    def __init__(self, url, feed_name):
        super(MISPCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["blacklist"])

    def download_raw_files(self, path):
        for i in range(6,9):
            os.system("wget "+self.url.replace("<level>", str(i))+" -P "+path+"/"+self.name)

    def merge_values(self, file_path, target_file_path, ioc_type):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        self.append_values(target_file_path, lines)


class OpenphishCollector(FeedCollector):
    def __init__(self, url, feed_name):
        super(OpenphishCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["http_uri"])

    def merge_values(self, file_path, target_file_path, ioc_type):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        self.append_values(target_file_path, lines)


class SSLCollector(FeedCollector):
    def __init__(self, url, feed_name):
        super(SSLCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["ssl_fingerprint"])

    def merge_values(self, file_path, target_file_path, ioc_type):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        new_lines = []
        for line in lines:
            if not "#" in line:
                new_lines.append(line.split(",")[0]+"\n")
        self.append_values(target_file_path, new_lines)


class SuricataCollector(FeedCollector):
    def __init__(self, url, feed_name):
        super(SuricataCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["bot", "tor"])

    def get_links(self, url, iptype):
        links_list = []
        resp = requests.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        for hlink in soup.findAll('a'):
            url_link = hlink.get('href')
            if iptype in url_link:
                links_list.append(url+url_link[2:])
        return(links_list)

    def download_raw_files(self, path):
        self.URI = []
        IPTypes = ["bot", "tor"]
        for iptype in IPTypes:
            self.URI.append(self.get_links(self.url, iptype)[0])
        for uri in self.URI:
            os.system("wget "+uri+" -P " +path+"/"+self.name)

    def clean_line(self, line):
        temp = ""
        start = False
        for i in line:
            if start and i != ']':
                temp += i
            if i == "]":
                break
            if i == "[":
                start = True 
        return temp.split(",")    

    def merge_values(self, file_path, target_file_path, ioc_type):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        new_lines = []
        for line in lines:
            if 'alert' in line:
                for ip in self.clean_line(line):
                    new_lines.append(ip.replace("\n", "")+"\n")
        self.append_values(target_file_path, new_lines)


class ThreatFoxCollector(FeedCollector):
    def __init__(self, url, feed_name):
        super(ThreatFoxCollector, self).__init__(url, feed_name)
        self.set_ioc_types(["domain"])

    def merge_values(self, file_path, target_file_path, ioc_type):
        f = open(file_path, "r")
        lines = f.readlines()
        f.close()
        new_lines = []
        for line in lines:
            if not "#" in line:
                new_line = line.replace(" ", "").replace("\t", "")[9:]
                new_lines.append(new_line)
        self.append_values(target_file_path, new_lines)

