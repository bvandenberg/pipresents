from glob import glob
import os
import csv
import json
import copy
import string
from pp_utils import Monitor

# *************************************
# MEDIALIST CLASS
# ************************************

class MediaList:
    """
    manages a media list of tracks and the track selected from the medialist
    """
    

    def __init__(self):
        self.clear()
        self.mon=Monitor()
        self.mon.on()
        
 # Functions for the editor dealing with complete list

    def clear(self):
        self._tracks = []  #MediaList, stored as a list of dicts
        self._num_tracks=0
        self._selected_track_index=-1 # index of currently selected track

    def print_list(self):
        print self._tracks

    def first(self):
        self.select(0)

    def length(self):
        return self._num_tracks

    def append(self, track_dict):
        """appends a track dictionary to the end of the medialist store"""
        self._tracks.append(copy.deepcopy(track_dict))
        self._num_tracks+=1

    def update(self,index,values):
        self._tracks[index].update(values)


    def remove(self,index):
        self._tracks.pop(index)
        self._num_tracks-=1
        # deselect any track, saves worrying about whether index needs changing
        self._selected_track_index=-1

    def move_up(self):
        if self._selected_track_index<>0:
            self._tracks.insert(self._selected_track_index-1, self._tracks.pop(self._selected_track_index))
            self.select(self._selected_track_index-1)

    def move_down(self):
        if self._selected_track_index<>self._num_tracks-1:
            self._tracks.insert(self._selected_track_index+1, self._tracks.pop(self._selected_track_index))
            self.select(self._selected_track_index+1)

    def replace(self,index,replacement):
        self._tracks[index]= replacement     
        
        
# Common functions work for anything
           

    def track_is_selected(self):
            if self._selected_track_index>=0:
                return True
            else:
                return False
            
    def selected_track_index(self):
        return self._selected_track_index

    def track(self,index):
        return self._tracks[index]
    
    def selected_track(self):
        """returns a dictionary containing all fields in the selected track """
        return self._selected_track

    def select(self,index):
        """does housekeeping necessary when a track is selected"""
        if self._num_tracks>0 and index>=0 and index< self._num_tracks:
            self._selected_track_index=index
            self._selected_track = self._tracks[index]
            return True
        else:
            return False

# Dealing with anonymous tracks for use and display

  
     
    def at_end(self):
        # true is selected track is last anon
        index=self._num_tracks-1
        while index>=0:
            if self._tracks[index] ['track-ref'] =="":
                end=index
                if self._selected_track_index==end:
                    return True
                else:
                    return False
            index -=1
        return False
        
        
    def index_of_end(self):
        index=self._num_tracks-1
        while index >= 0:
            if self._tracks[index] ['track-ref'] =="":
                return index
            index -=1
        return -1
   
   
    def at_start(self):
        index=0
        while index<self._num_tracks:
            if self._tracks[index] ['track-ref'] =="":
                start =  index
                if self._selected_track_index==start:
                    return True
                else:
                    return False
            index +=1
        return False
   
            
    def index_of_start(self):
        index=0
        while index<self._num_tracks:
            if self._tracks[index] ['track-ref'] =="":
                return index
            index +=1
        return False


    def display_length(self):
        count=0
        index=0
        while index<self._num_tracks:
            if self._tracks[index] ['track-ref'] =="":
                count+=1
            index +=1
        return count

    def start(self):
        # select first anymous track in the list
        index=0
        while index<self._num_tracks:
            if self._tracks[index] ['track-ref'] =="":
                self.select(index)
                return True
            index +=1
        return False

    def finish(self):
        # select first anymous track in the list
        index=self._num_tracks-1
        while index>=0:
            if self._tracks[index] ['track-ref'] =="":
                self.select(index)
                return True
            index -=1
        return False

    def next(self):
        if self._selected_track_index== self._num_tracks-1:
            index=0
        else:
            index= self._selected_track_index+1
        end=self._selected_track_index
        while index<>end:
            if self._tracks[index] ['track-ref'] =="":
                self.select(index)
                return True
            if index== self._num_tracks-1:
                index=0
            else:
                index= index+1
        return False

    def previous(self):
        if self._selected_track_index == 0:
            index=self._num_tracks-1
        else:
            index= self._selected_track_index-1
        end = self._selected_track_index 
        while index<>end :
            if self._tracks[index] ['track-ref'] =="":
                self.select(index)
                return True                
            if index == 0:
                index=self._num_tracks-1
            else:
                index= index-1
        return False
    
    
# Lookup for labelled tracks
    
    
    def index_of_track(self,wanted_track):
        index = 0
        for track in self._tracks:
            if track['track-ref']==wanted_track:
                return index
            index +=1
        return -1


# open and save


    def open_list(self,filename,showlist_issue):
        """
        opens a saved medialist
        medialists are stored as json arrays.
        """
        ifile  = open(filename, 'rb')
        mdict = json.load(ifile)
        ifile.close()
        self._tracks = mdict['tracks']
        if 'issue' in mdict:
            self.issue= mdict['issue']
        else:
            self.issue="1.0"
        if self.issue==showlist_issue:
            self._num_tracks=len(self._tracks)
            self._selected_track_index=-1
            return True
        else:
            return False

    def issue(self):
        return self.issue

    def save_list(self,filename):
        """ save a medialist """
        if filename=="":
            return False
        dic={'issue':self.issue,'tracks':self._tracks}
        filename=str(filename)
        filename = string.replace(filename,'\\','/')
        tries = 1
        while tries<=10:
            # print "save  medialist  ",filename
            try:
                ofile  = open(filename, "wb")
                json.dump(dic,ofile,sort_keys=True,indent=1)
                ofile.close()
                self.mon.log(self,"Saved medialist "+ filename)
                break
            except IOError:
                self.mon.err(self,"failed to save medialist, trying again " + str(tries))
                tries+=1
        return


# for the future

    def open_csv(self,filename):
        """
        opens a saved csv medialist
        """
        if filename !="" and os.path.exists(filename):
            ifile  = open(filename, 'rb')
            pl=csv.reader(ifile)
            for pl_row in pl:
                if len(pl_row) != 0:
                    entry=dict([('type',pl_row[2]),('location',pl_row[0]),('title',pl_row[1])])
                    self.append(copy.deepcopy(entry))
            ifile.close()
            return True
        else:
            return False

