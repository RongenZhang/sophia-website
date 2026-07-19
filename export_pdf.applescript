-- Exports a .docx to .pdf using Microsoft Word.
-- Usage: osascript export_pdf.applescript "/path/in.docx" "/path/out.pdf"
-- Called by build.py when the latest CV has no matching PDF.
on run argv
	set inPath to item 1 of argv
	set outPath to item 2 of argv
	tell application "Microsoft Word"
		set wasRunning to running
		with timeout of 300 seconds
			open inPath
			set theDoc to active document
			save as theDoc file name outPath file format format PDF
			close theDoc saving no
			if not wasRunning then quit saving no
		end timeout
	end tell
end run
