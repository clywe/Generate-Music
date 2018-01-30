import guitarpro
import time


def transpose2GP5file(track, totaldict):
    '''
    Function to take an empty gp5 song and fill with song information
    from dictionary generated from txt2songDict function
    '''
    meas = 1
    breakMeas = float('Inf')
    for measure in track.measures:
        #measure.keySignature = totaldict['measure_'+str(meas)]['key']
        #measure.length = totaldict['measure_'+str(meas)]['mlen']
        #measure.start = totaldict['measure_'+str(meas)]['mstart']
        for voice in measure.voices:
            try:
                beats_list = totaldict['measure_'+str(meas)]['beats']
                thebeat = 0
            except KeyError:
                if meas < breakMeas:
                    breakMeas = meas
                break
            for beat in voice.beats:
                beat.start = beats_list[thebeat]
                try:
                    strings = totaldict['measure_'+str(meas)]['strings'+str(beats_list[thebeat])]
                    realValues = totaldict['measure_'+str(meas)]['Notes'+str(beats_list[thebeat])]
                except KeyError:
                    break
                notes = []
                for string, realValue in zip(strings, realValues):
                    note = guitarpro.models.Note(thebeat)
                    note.string = string
                    note.value = realValue
                                        notes.append(note)
                beat.notes = notes
            thebeat += 1
        meas += 1
    #track.measures = track.measures[:breakMeas-1]
    return(track)

# ================================================================================

def main():
    def txt2songDict(track):
        '''
        Read txt file and go through line by line
        convert all information into dictionary of measures
        '''
        #    myfile =open('xyz.txt', 'r')
        with open(track) as f:
            total_dict = {}
            measures_list = []
            measNum = 0
            measStart = 0
            key = 'CMajor'
            song_len = 3840
            for line in f:
                if line[:5] == 'strgs':

                    fc1 = line.find('fc')
                    try:
                        strings = line[6:fc1].split()
                    except ValueError:
                        break
                    key1 = line.find('Key')
                    fc = line[fc1+4:key1]
                    len1 = line.find('len')
                    key = line[key1+13:len1-1]
                    tempo1 = line.find('tmpo')
                    song_len = line[len1+4:tempo1]
                    try:
                        tempo = line[tempo1+5:tempo1+7]
                    except ValueError:
                        tempo = line[tempo1+5:tempo1+6]
                    init_dict = {}
                    init_dict['tempo'] = tempo
                    gpStrings = [guitarpro.models.GuitarString(number, string) for number, string in enumerate(strings)]
                    init_dict['string'] = gpStrings
                    init_dict['fretCount'] = fc
                    total_dict['init_dict'] = init_dict
                elif line[:3] == 'Num':
                    measStart1 = line.find('mst')
                    if measNum > 0:
                        total_dict['measure_'+str(measNum)]['beats'] = beats
                    measNum += 1
                    measStart += 3840
                    meas_dict = {}
                    meas_dict['key'] = key
                    meas_dict['mlen'] = song_len
                    meas_dict['mstart'] = measStart
                    measures_list.append(meas_dict)
                    total_dict['measure_'+str(measNum)] = meas_dict
                    beats = []

                elif line[:3] == 'vst':
                    beatStart1 = measStart + 221820-int(line[4:11])
                    beats.append(beatStart1)
                    strings = []
                    notes = []
                elif line[:1] == 'S' and line[2] != 'n':
                    valStart = line.find('V')
                    string = int(line[2])
                    realVal = int(line[valStart+2:valStart+5])
                    strings.append(string)
                    notes.append(realVal)
                    total_dict['measure_'+str(measNum)]['strings' + str(beatStart1)] = strings
                    total_dict['measure_'+str(measNum)]['Notes' + str(beatStart1)]= notes


        return(total_dict)

    curl = guitarpro.parse('Serenade.gp5')
    track = curl.tracks[0]
    for measure in track.measures:
        for voice in measure.voices:
            for beat in voice.beats:
                beat.notes = []
    curl.tracks[0] = track

    songDict = txt2songDict('sample.txt')
    track = curl.tracks[0]
    track = transpose2GP5file(track, songDict)
    curl.tracks[0] = track
    curl.artist = 'R. N. Net'
    curl.album = time.strftime("%d %B %Y")
    curl.title = 'Metallica Style Song'
    guitarpro.write(curl, 'genMetallica.gp5')

if __name__ == '__main__':
    main()
