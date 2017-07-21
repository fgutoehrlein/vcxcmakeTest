import re
from settings import *

print('vcx to cmake regex script')
cmakelists=open(CMakeListsPath,'w')
vcxproj=open(ProjectFilePath)
cmakelists.write('project(%s)\n\n' %(ProjectName))

#Search for MFC option
def findMFC():
    MFC = 0
    pattern = re.compile("<UseOfMfc>Static</UseOfMfc>")
    for i, line in enumerate(open(ProjectFilePath)):
        m = pattern.search(line)
        if m is not None:
            MFC = 1
    if MFC == 1:
        print('Found MFC option')
        cmakelists.write('set(CMAKE_MFC_FLAG 1)\n\n')

    pattern = re.compile("<UseOfMfc>Dynamic</UseOfMfc>")
    for i, line in enumerate(open(ProjectFilePath)):
        m = pattern.search(line)
        if m is not None:
            MFC = 2
    if MFC == 2:
        print('Found MFC option')
        cmakelists.write('set(CMAKE_MFC_FLAG 2)\n\n')

#Search for include files
def findIncludes():
    pattern = re.compile("<ClCompile\sInclude=\"([^<]*)\"")
    cmakelists.write('set(SOURCE_FILES\n')
    for i, line in enumerate(open(ProjectFilePath)):
        for match in re.finditer(pattern, line):
            for string in match.groups():
                foundInclude=string.replace('\\','/')
                includeFound=True
            cmakelists.write('    "%s"\n' % (foundInclude))
    if includeFound:
        print('Found source files')

            #print('Found on line %s: %s:' % (i + 1, match.groups()))

    pattern = re.compile("<ResourceCompile\sInclude=\"([^<]*)\"")
    for i, line in enumerate(open(ProjectFilePath)):
        for match in re.finditer(pattern, line):
            for string in match.groups():
                foundInclude=string.replace('\\','/')
                recourceFound=True
            cmakelists.write('    "%s"\n' % (foundInclude))
            #print('Found on line %s: %s:' % (i + 1, match.groups()))
    if recourceFound:
        print('Found resource files')

    pattern = re.compile("<None Include=\"([^<]*)\.def\"")
    for i, line in enumerate(open(ProjectFilePath)):
        for match in re.finditer(pattern, line):
            for string in match.groups():
                foundInclude = string.replace('\\', '/')
                defFileFound = True
            cmakelists.write('    "%s.def"\n' % (foundInclude))
            # print('Found on line %s: %s:' % (i + 1, match.groups()))
    if defFileFound:
        print('Found def files')
    cmakelists.write(')\n\n')

#Add the target
def addTarget():
    dynamic = 0
    cmakelists.write('add_library(%s ' % (ProjectName))
    pattern = re.compile("<ConfigurationType>DynamicLibrary</ConfigurationType>")
    for i, line in enumerate(open(ProjectFilePath)):
        m = pattern.search(line)
        if m is not None:
            dynamic = 1
    if dynamic == 1:
        cmakelists.write('SHARED')
        print('Target added as dll')

    static = 0
    pattern = re.compile("<ConfigurationType>StaticLibrary</ConfigurationType>")

    for i, line in enumerate(open(ProjectFilePath)):
        m = pattern.search(line)
        if m is not None:
            static = 1
    if static == 1:
        cmakelists.write('STATIC')
        print('Target added as lib')

    if static != 1 & dynamic !=1:
        cmakelists.write('add_executable(%s ' %(ProjectName))
        print('Target added as exe')
    cmakelists.write(' ${SOURCE_FILES})\n\n')
    if static ==1 & dynamic ==1:
        print('TARGET ERROR')

#Search for dependencies
def findDependencies():
    pattern = re.compile("<ProjectReference\sInclude=\".*\\\([^<]*)\.vcxproj\"")
    cmakelists.write('add_dependencies(%s ' % (ProjectName))
    for i, line in enumerate(open(ProjectFilePath)):
        for match in re.finditer(pattern, line):
            for string in match.groups():
                foundDependency = string.replace('\\', '/')
                dependencyFound = True
            cmakelists.write('%s' % (foundDependency))
    if dependencyFound:
        print('Found dependencies')
        cmakelists.write(')\n')
    elif dependencyFound==False:
        pattern = re.compile("<ProjectReference\sInclude=\"([^<]*)\.vcxproj\"")
        cmakelists.write('add_dependencies(%s ' % (ProjectName))
        for i, line in enumerate(open(ProjectFilePath)):
            for match in re.finditer(pattern, line):
                for string in match.groups():
                    foundDependency = string.replace('\\', '/')
                    dependencyFound = True
                cmakelists.write('%s' % (foundDependency))
        print('Found dependencies')
        cmakelists.write(')\n')

#Find preprocessor definitions
def findCompileDefinitions():
    endOfFile=False
    debugFound=False
    # Search for Debug definitions
    while(debugFound==False | endOfFile==False):
        configPattern = re.compile("<ItemDefinitionGroup\sCondition=\"'\$\(Configuration\)\|\$\(Platform\)'=='.*(Debug\|Win32).*'\">")
        for i, line in enumerate(open(ProjectFilePath)):
            for match in re.finditer(configPattern, line):
                tmpLine = i
        for i,line in enumerate(open(ProjectFilePath)):
            if i>tmpLine:
                pattern = re.compile("<PreprocessorDefinitions>WIN32([^<]*)</PreprocessorDefinitions>")
                for match in re.finditer(pattern, line):
                    print('Found x32 debug Preprocessor Definitions')
                    tmpDefinitions = match.groups()
                    for string in tmpDefinitions:
                        cmakelists.write('\n#Win32 Debug Preprocessor Definitions\n')
                        cmakelists.write('target_compile_definitions(%s PRIVATE\n $<$<CONFIG:Debug>:' % (ProjectName))
                        definitionsString = string.replace(';', ' ')
                        definitionsString = definitionsString.replace('%(PreprocessorDefinitions)', '')
                        cmakelists.write('WIN32%s>)' % (definitionsString))
                        debugFound = True
            if debugFound==True:
                break
        endOfFile=True

    endOfFile=False
    debugFound=False
    tmpLine=0
    while(debugFound==False | endOfFile==False):
        configPattern = re.compile("<ItemDefinitionGroup\sCondition=\"'\$\(Configuration\)\|\$\(Platform\)'=='.*(Debug\|x64).*'\">")
        for i, line in enumerate(open(ProjectFilePath)):
            for match in re.finditer(configPattern, line):
                tmpLine = i
        for i,line in enumerate(open(ProjectFilePath)):
            if i>tmpLine:
                pattern = re.compile("<PreprocessorDefinitions>WIN64([^<]*)</PreprocessorDefinitions>")
                for match in re.finditer(pattern, line):
                    print('Found x64 debug Preprocessor Definitions')
                    tmpDefinitions = match.groups()
                    for string in tmpDefinitions:
                        cmakelists.write('\n#Win64 Debug Preprocessor Definitions\n')
                        cmakelists.write('target_compile_definitions(%s PRIVATE\n $<$<CONFIG:Debug>:' % (ProjectName))
                        definitionsString = string.replace(';', ' ')
                        definitionsString = definitionsString.replace('%(PreprocessorDefinitions)', '')
                        cmakelists.write('WIN64%s>)' % (definitionsString))
                        debugFound = True
            if debugFound==True:
                break
        endOfFile = True

    #Search for Release definitions
    endOfFile = False
    releaseFound=False
    tmpLine=0
    while(releaseFound==False | endOfFile==False):
        configPattern = re.compile(
            "<ItemDefinitionGroup\sCondition=\"'\$\(Configuration\)\|\$\(Platform\)'=='.*(Release\|Win32).*'\">")
        for i, line in enumerate(open(ProjectFilePath)):
            for match in re.finditer(configPattern, line):
                tmpLine = i
        for i,line in enumerate(open(ProjectFilePath)):
            if i>tmpLine:
                pattern = re.compile("<PreprocessorDefinitions>WIN32([^<]*)</PreprocessorDefinitions>")
                for match in re.finditer(pattern, line):
                    print('Found x32 release Preprocessor Definitions')
                    tmpDefinitions = match.groups()
                    for string in tmpDefinitions:
                        cmakelists.write('\n#Win32 Release Preprocessor Definitions\n')
                        cmakelists.write('target_compile_definitions(%s PRIVATE\n $<$<NOT:$<CONFIG:Debug>>:' % (ProjectName))
                        definitionsString = string.replace(';', ' ')
                        definitionsString = definitionsString.replace('%(PreprocessorDefinitions)', '')
                        cmakelists.write('WIN32%s>)' % (definitionsString))
                        releaseFound = True
            if releaseFound==True:
                break
        endOfFile=True

    endOfFile=False
    releaseFound=False
    tmpLine=0
    while(releaseFound==False | endOfFile==False):
        configPattern = re.compile(
            "<ItemDefinitionGroup\sCondition=\"'\$\(Configuration\)\|\$\(Platform\)'=='.*(Release\|x64).*'\">")
        for i, line in enumerate(open(ProjectFilePath)):
            for match in re.finditer(configPattern, line):
                tmpLine = i
        for i,line in enumerate(open(ProjectFilePath)):
            if i>tmpLine:
                pattern = re.compile("<PreprocessorDefinitions>WIN64([^<]*)</PreprocessorDefinitions>")
                for match in re.finditer(pattern, line):
                    print('Found x64 release Preprocessor Definitions')
                    tmpDefinitions = match.groups()
                    for string in tmpDefinitions:
                        cmakelists.write('\n#Win64 Release Preprocessor Definitions\n')
                        cmakelists.write('target_compile_definitions(%s PRIVATE\n $<$<NOT:$<CONFIG:Debug>>:' % (ProjectName))
                        definitionsString = string.replace(';', ' ')
                        definitionsString = definitionsString.replace('%(PreprocessorDefinitions)', '')
                        cmakelists.write('WIN64%s>)' % (definitionsString))
                        releaseFound = True
            if releaseFound==True:
                break
        endOfFile=True

#Check for specified runtime library
def findRuntimeLibrary():
    MT = 0
    #pattern = re.compile("<UseOfMfc>Static</UseOfMfc>")
    pattern = re.compile("<RuntimeLibrary>MultiThreadedDebugDLL</RuntimeLibrary>")
    for i, line in enumerate(open(ProjectFilePath)):
        m = pattern.search(line)
        if m is not None:
            MT = 1
    if MT == 1:
        cmakelists.write('#Added Multithreaded Dll')
        cmakelists.write('\ntarget_compile_options(%s PRIVATE "$<$<CONFIG:Debug>:/MDd>" "$<$<NOT:$<CONFIG:Debug>>:/MD>")\n\n' % (ProjectName))


    pattern = re.compile("<RuntimeLibrary>MultiThreadedDebug</RuntimeLibrary>")
    for i, line in enumerate(open(ProjectFilePath)):
        m = pattern.search(line)
        if m is not None:
            MT = 2
    if MT == 2:
        cmakelists.write('#Added Multithreaded')
        cmakelists.write('\ntarget_compile_options(%s PRIVATE "$<$<CONFIG:Debug>:/MTd>" "$<$<NOT:$<CONFIG:Debug>>:/MT>")\n\n' % (ProjectName))

#Search for additional directories
def findAdditionalDirectories():
    foundDirectories = False
    pattern = re.compile("<AdditionalIncludeDirectories>([^<]*)\%\(AdditionalIncludeDirectories\)</AdditionalIncludeDirectories>")
    cmakelists.write('target_include_directories(%s PRIVATE\n' % (ProjectName))
    for i, line in enumerate(open(ProjectFilePath)):
        for match in re.finditer(pattern, line):
            for string in match.groups():
                foundDirectories = True
                additionalDirs = string.replace('\\', '/')
                additionalDirs = additionalDirs.replace(CurrentDirectoryVariable,'${CMAKE_CURRENT_LIST_DIR}/')
                additionalDirs = additionalDirs.replace(RootDirectoryVariable, '${CMAKE_SOURCE_DIR}/')
                additionalDirs = additionalDirs.replace(';', '"\n"')
            cmakelists.write('"%s")\n\n' % (additionalDirs))
        if foundDirectories:
            break
    if foundDirectories:
        print('Found additional directories')

#Search for additional libraries
def findAdditionalLibraries():
    foundLibraries = False
    pattern = re.compile("<AdditionalDependencies>([^<]*)</AdditionalDependencies>")
    cmakelists.write('\n#Use debug and optimize to let CMake know for which config the Libraries are\n')
    cmakelists.write('target_link_libraries(%s PRIVATE\n' % (ProjectName))
    for i, line in enumerate(open(ProjectFilePath)):
        for match in re.finditer(pattern, line):
            foundLibraries = True
            for string in match.groups():
                additionalLibraries=string.replace('\\','/')
                additionalLibraries = additionalLibraries.replace('%(AdditionalDependencies)', '')
                additionalLibraries=additionalLibraries.replace(';','"\n    "')
            cmakelists.write('    "%s"\n' % (additionalLibraries))
        if foundLibraries:
            break
    if foundLibraries:
        print('Found additional libraries')

#Search for included libraries
def findIncludedLibraries():
    pattern = re.compile("<Library\sInclude=\"([^<]*)\"")
    for i, line in enumerate(open(ProjectFilePath)):
        for match in re.finditer(pattern, line):
            for string in match.groups():
                librariesFound=True
                foundLibrary=string.replace('\\','/')
            cmakelists.write('    "%s"\n' % (foundLibrary))
            #print('Found on line %s: %s:' % (i + 1, match.groups()))
    cmakelists.write(')\n\n')
    if librariesFound:
        print('Found included libraries')

#Search for ignored default libraries
def findIgnoredLibraries():
    debugFound=False
    # Search for Debug definitions
    configPattern = re.compile("<ItemDefinitionGroup\sCondition=\"'\$\(Configuration\)\|\$\(Platform\)'=='.*(Debug).*'\">")
    for i, line in enumerate(open(ProjectFilePath)):
        for match in re.finditer(configPattern,line):
            pattern = re.compile("<IgnoreSpecificDefaultLibraries>([^<]*);\%\(IgnoreSpecificDefaultLibraries\)</IgnoreSpecificDefaultLibraries>")
            for i, line in enumerate(open(ProjectFilePath)):
                for match in re.finditer(pattern, line):
                    cmakelists.write('set_target_properties(%s PROPERTIES\n    LINK_FLAGS_DEBUG "/NODEFAULTLIB:' %(ProjectName))
                    tmpDefinitions = match.groups()
                    for string in tmpDefinitions:
                        ignoredLibraries = string.replace(';', '/NODEFAULTLIB:')
                        cmakelists.write(ignoredLibraries)
                        cmakelists.write('")\n')
                        debugFound = True
                if debugFound:
                    break
            if debugFound:
                break
        if debugFound:
            break
    if debugFound:
        print('Found ignored libraries for debug')
    releaseFound=False
    endOfFile=False
    # Search for Release definitions
    while(releaseFound==False | endOfFile==False):
        configPattern = re.compile("<ItemDefinitionGroup\sCondition=\"'\$\(Configuration\)\|\$\(Platform\)'=='.*(Release).*'\">")
        for i, line in enumerate(open(ProjectFilePath)):
            for match in re.finditer(configPattern, line):
                tmpLine = i
        for i,line in enumerate(open(ProjectFilePath)):
            if i>tmpLine:
                pattern = re.compile("<IgnoreSpecificDefaultLibraries>([^<]*);\%\(IgnoreSpecificDefaultLibraries\)</IgnoreSpecificDefaultLibraries>")
                for match in re.finditer(pattern, line):
                    cmakelists.write('set_target_properties(%s PROPERTIES\n    LINK_FLAGS_RELEASE "/NODEFAULTLIB:' % (ProjectName))
                    tmpDefinitions = match.groups()
                    for string in tmpDefinitions:
                        ignoredLibraries = string.replace(';', '/NODEFAULTLIB:')
                        cmakelists.write(ignoredLibraries)
                        cmakelists.write('")\n')
                        releaseFound = True
        if releaseFound:
            print('Found ignored libraries for release')
        endOfFile=True

#Execute Functions

findMFC()
findIncludes()
addTarget()
findDependencies()
findCompileDefinitions()
findRuntimeLibrary()
findAdditionalDirectories()
findAdditionalLibraries()
findIncludedLibraries()
findIgnoredLibraries()

cmakelists.write('unset(CMAKE_MFC_FLAG)')

