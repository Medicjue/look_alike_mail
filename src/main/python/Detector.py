# -*- coding: utf-8 -*-

import re
import tldextract
import editdistance

class Detector:
    
    def __init__(self):
        self.substr_edit_distance = 5
        self.substr_jaccard_sim = 0.5
        self.non_substr_edit_distance = 1
        self.non_substr_jaccard_sim = 0.5
        self.allow_diff_tld = False
        self.domain_cnt_threshold = 10
        self.email_regex = '(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
        self.acct_edit_distance_threshold = 2
        self.acct_jaccard_sim_threshold = 0.5

        
    def decompose_email_address(self, mail_addr):
        if re.match(self.email_regex, mail_addr):
            return mail_addr.split('@')
        else:
            raise ValueError('Email format is invalid')
            
    def decompose_email_domain(self, mail_domain):
        tldextract_result = tldextract.extract(mail_domain)
        return tldextract_result.subdomain, tldextract_result.domain, tldextract_result.suffix
    
    def cal_jaccard_sim(self, word1, word2):
        return len(set(word1).intersection(set(word2))) / len(set(word1).union(set(word2)))
    def check_substr(self, word1, word2):
        is_substr = True if word1 in word2 or word2 in word1 else False
        substr_index = word1.find(word2) if word1.find(word2) > word2.find(word1) else word2.find(word1)
        return is_substr, substr_index
        
    def detect(self, base_mail_addr, domain_cnt_history, email_history):
        base_mail_acct, base_mail_domain = self.decompose_email_address(self, base_mail_addr)
        base_subdomain, base_main_domain, base_tld = self.decompose_email_domain(self, base_mail_domain)
        base_mail_suffix = base_main_domain + '.' + base_tld
        base_domain_cnt = domain_cnt_history.get(base_mail_domain, 0)
        if base_domain_cnt <= self.domain_cnt_threshold:
            for cmp_mail_domain, cmp_domain_cnt in domain_cnt_history.items():
                if cmp_mail_domain == base_mail_domain:
                    return False, 'Same Mail Domain'
                cmp_subdomain, cmp_main_domain, cmp_tld = self.decompose_email_domain(self, cmp_mail_domain)
                cmp_mail_suffix = cmp_main_domain + '.' + cmp_tld
                if cmp_mail_suffix == base_mail_suffix:
                    return False, 'Same Mail Suffix'
                
                domain_edit_distance = editdistance.eval(base_main_domain, cmp_main_domain)
                domain_jaccard_sim = self.cal_jaccard_sim(self, base_main_domain, cmp_main_domain)
                
                is_substr, substr_index = self.check_substr(self, base_main_domain, cmp_main_domain)
                
                cond_1 = is_substr and substr_index == 0 and domain_edit_distance <= self.substr_edit_distance and domain_jaccard_sim < self.substr_jaccard_sim 
                cond_2 = not is_substr and domain_edit_distance <= self.non_substr_edit_distance and domain_jaccard_sim < self.non_substr_jaccard_sim 
                if cond_1 or cond_2:
                    is_acct_similar = self.detect_mail_acct(self, base_mail_acct, cmp_mail_domain, email_history)
                    return is_acct_similar
                
    def detect_mail_acct(self, base_mail_acct, cmp_mail_domain, email_history):
        given_domain_history = [mail for mail in email_history if mail['domain'] == cmp_mail_domain]
        for cmp_mail in given_domain_history:
            cmp_mail_acct = cmp_mail['acct']
            acct_edit_distance = editdistance.eval(base_mail_acct, cmp_mail_acct)
            acct_jaccard_sim = self.cal_jaccard_sim(self, base_mail_acct, cmp_mail_acct)
            if acct_edit_distance <= self.acct_edit_distance_threshold and acct_jaccard_sim > self.acct_jaccard_sim_threshold:
                return True
        return False