function Header(el)
  if el.level == 1 then
    return pandoc.Div({pandoc.Para(el.content)}, {["custom-style"] = "Title"})
  end
  el.level = el.level - 1
  return el
end

function Para(el)
  if pandoc.utils.stringify(el) == "[TOC]" then return {} end
  return el
end

function Link(el)
  local text = pandoc.utils.stringify(el.content)
  if string.match(text, "^%d+$") then
    el.content = {pandoc.Str("[" .. text .. "]")}
  end
  return el
end
