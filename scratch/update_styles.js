const fs = require('fs');
const path = require('path');

const componentsDir = 'd:/METGO_3D_Quillota_60GB/frontend/vue/src/components';

const replacements = [
    [/stroke="#e5e7eb"/g, 'stroke="var(--color-border, #334155)"'],
    [/stroke="#f3f4f6"/g, 'stroke="var(--color-surface, #1e293b)"'],
    [/stroke="#fff"/g, 'stroke="var(--color-background, #0f172a)"'],
    [/stroke="#ffffff"/g, 'stroke="var(--color-background, #0f172a)"'],
    [/fill="#fff"/g, 'fill="var(--color-background, #0f172a)"'],
    [/fill="#ffffff"/g, 'fill="var(--color-background, #0f172a)"'],
    [/fill="#6b7280"/g, 'fill="var(--color-text-muted, #94a3b8)"'],
    [/color:\s*#6b7280/g, 'color: var(--color-text-muted, #94a3b8)'],
    [/background:\s*#ffffff/g, 'background: var(--color-surface, #1e293b)'],
    [/background-color:\s*#ffffff/g, 'background-color: var(--color-surface, #1e293b)'],
    [/background:\s*#f9fafb/g, 'background: var(--color-background, #0f172a)'],
    [/border:\s*1px\s+solid\s+#e5e7eb/g, 'border: 1px solid var(--color-border, #334155)'],
    [/border-top:\s*1px\s+solid\s+#e5e7eb/g, 'border-top: 1px solid var(--color-border, #334155)'],
    [/border-bottom:\s*1px\s+solid\s+#e5e7eb/g, 'border-bottom: 1px solid var(--color-border, #334155)'],
    [/border-color:\s*#e5e7eb/g, 'border-color: var(--color-border, #334155)'],
];

function processDirectory(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            processDirectory(fullPath);
        } else if (file.endsWith('.vue')) {
            let content = fs.readFileSync(fullPath, 'utf8');
            let newContent = content;
            for (const [regex, replacement] of replacements) {
                newContent = newContent.replace(regex, replacement);
            }
            if (newContent !== content) {
                fs.writeFileSync(fullPath, newContent, 'utf8');
                console.log(`Updated ${file}`);
            }
        }
    }
}

processDirectory(componentsDir);
console.log('Done.');
