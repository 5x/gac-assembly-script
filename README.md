# gac-assembly-script

Simple automated script for building signed assemblies on .NET Framework.

Script check installed versions of .NET Framework and select a recent possible version.
Sign component with Strong Name Tool and compile C# module, after creating a linked 
assembly with optional opportunity install to GAC (require UAC, admin permission). 
Output assemblies placed in the `assemblies` subfolder of the working directory.

## Usage example
```
[INFO] Available .Net versions: ['2.0.50727', '3.0', '3.5', '4', '4.0']
[INFO] DonNET SDK folder: C:\Program Files (x86)\Microsoft SDKs\Windows\v7.0A\
[INFO] DonNET Framework Compiler path: C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe
[USER] Source files path
> D:\Projects\2017_ApplicationsCP\BankAccountLib
[INFO] Source files:
\Account.cs
\EnvInfo.cs
\IAccount.cs
\Properties\AssemblyInfo.cs
[USER] Enter component name(default BankAccountLib): NZEBankAccountComponent
[DONE] Check output directory: D:\Projects\2017_GAC\dist\out
[DONE] Strong key pair created: NZEBankAccountComponent.snk
[DONE] DotNET module compiled: NZEBankAccountComponent.netmodule
[DONE] Assembly successful linked: NZEBankAccountComponent.dll
[USER] Install to GAC(Default no)[Y, n]: Y
Assembly successfully added to the cache
[DONE] Install assembly to GAC.
The Global Assembly Cache contains the following assemblies:
  NZEBankAccountComponent, Version=1.0.0.0, Culture=neutral, PublicKeyToken=266683df4fb10a4f, processorArchitecture=MSIL

Number of items = 1
Success. 

Press ENTER to exit.
```

## Build Windows Application 

To create runnable execute application use next:
```bash
pyinstaller --onefile --console gac.py
```
[More info about PyInstaller](https://www.pyinstaller.org/)

## Requirements

* Python 3.4 or later
* pyinstaller

## Support & Contributing
Anyone is welcome to contribute. If you decide to get involved, please take a moment and check out the following:

* [Bug reports](.github/ISSUE_TEMPLATE/bug_report.md)
* [Feature requests](.github/ISSUE_TEMPLATE/feature_request.md)

## License

The code is available under the [MIT license](LICENSE).
