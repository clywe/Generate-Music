import guitarpro
from os import listdir


def unfold_tracknumber(tracknumber, tracks):
    """Substitute '*' with all track numbers except for percussion tracks."""
    if tracknumber == '*':
        for number, track in enumerate(tracks, start=1):
            if not track.isPercussionTrack:
                yield number
    else:
        yield tracknumber


def transpose(myfile, track):
    '''
    Get pertinent information from guitar pro files and write to text file
    '''
    myfile.write("%s" % 'strgs: ' +' '.join([str(string) for string in track.strings]) + ' ')
    myfile.write("%s" % 'fc: ' +str(track.fretCount) + ' ')
    measure1 = track.measures[0]
    myfile.write("%s" % str(measure1.keySignature) + ' ')
    myfile.write("%s" % 'len:' + str(measure1.length) + ' ')
    myfile.write("%s" % 'tmpo:' + str(measure1.tempo) + '\n')
    i = 1
    for measure in track.measures:
        myfile.write("%s" % 'Num:' + str(i) + ' ')
        myfile.write("%s" % 'mst:' + str(measure.start) + '\n')
        for voice in measure.voices:
            for beat in voice.beats:
                myfile.write("%s" % 'vst:' + str(beat.start) + '\n')
                for note in beat.notes:
                    myfile.write("%s" % 'S:' + str(note.string) + ' ')
                    myfile.write("%s" % 'V:' + str(note.value) + '\n')
        i += 1

# =================================================================

def main():

    band = 'system of a down'
    mydir = 'out/' + band
    files = listdir(mydir)
    myfile = open('sample.txt', 'w')
    for gpfile in files:
        try:
            curl = guitarpro.parse(mydir + '/'+ gpfile)
            transpose(myfile, curl.tracks[0])
            stro = str(curl).replace(',',',\n')
            myfile.write(stro)
            myfile.write('\n\r\n\r')
            print (gpfile)
        except:
            print ("Error : " + gpfile)


    myfile.close()

if __name__== '__main__':
    main()
    print ("Success")
