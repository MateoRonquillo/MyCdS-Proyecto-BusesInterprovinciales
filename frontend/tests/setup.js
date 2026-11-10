import { vi } from 'vitest'
Object.defineProperty(window,'matchMedia',{writable:true,value:vi.fn(query=>({matches:false,media:query,addEventListener:vi.fn(),removeEventListener:vi.fn()}))})
HTMLDialogElement.prototype.showModal=function(){this.open=true}
HTMLDialogElement.prototype.close=function(){this.open=false;this.dispatchEvent(new Event('close'))}
HTMLMediaElement.prototype.play=vi.fn(async()=>{})
