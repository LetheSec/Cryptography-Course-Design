import gmpy2
import libnum
e = 3
n= 22885480907469109159947272333565375109310485067211461543881386718201442106967914852474989176175269612229966461160065872310916096148216253429849921988412342732706875998100337754561586600637594798877898552625378551427864501926224989873772743227733285336042475675299391051376624685754547818835551263597996620383338263448888107691240136257201191331617560711786674975909597833383395574686942099700631002290836152972352041024137872983284691831292216787307841877839674258086005814225532597955826353796634417780156185485054141684249037538570742860026295194559710972266059844824388916869414355952432189722465103299013237588737
c= 15685364647213619014219110070569189770745535885901269792039052046431067708991036961644224230125219358149236447900927116989931929305133870392430610563331490276096858863490412102016758082433435355613099047001069687409209484751075897343335693872741
print('n=', n)
print('c=', c)
result = gmpy2.iroot(c, 3)
if result[1]:
    print('m= ',libnum.n2s(result[0]))




